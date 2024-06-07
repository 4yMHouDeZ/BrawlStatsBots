from credits import bs_key
from credits import tg_token as bot_token
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
import requests

application = Application.builder().token(bot_token).build()


# hex to rgb
def hex_to_rgb(h: str) -> [int, int, int]:
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# Глобальный топ игроков
async def top(update: Update, context: CallbackContext):
    limit = update.message.text.split()[-1]
    top_ = requests.get(
        f'https://api.brawlstars.com/v1/rankings/global/players',
        headers={'Authorization': f'Bearer {bs_key}'}
    ).json()
    players = [i for i in top_['items'] if i['rank'] <= int(limit)]
    descr = f'Топ-{limit} игроков\n - ' + "\n - ".join([i['name'] for i in players])
    await update.message.chat.send_message(descr)


# Отображает основную информацию об аккаунте
async def info(update: Update, context: CallbackContext):
    player_tag = update.message.text.split()[1]
    profile = requests.get(
        f'https://api.brawlstars.com/v1/players/%23{player_tag}',
        headers={'Authorization': f'Bearer {bs_key}'}
    ).json()
    descr = (f"{profile['name']}\n"
             f"Тег: {profile['tag']}\nТрофеев: {profile['trophies']}\n"
             f"Побед всего: {profile['3vs3Victories'] + profile['soloVictories'] + profile['duoVictories']}\n"
             f" - Сольные победы: {profile['soloVictories']}\n- Парные победы: {profile['duoVictories']}\n"
             f"- Командные победы: {profile['3vs3Victories']}")

    keyboard = [
        [InlineKeyboardButton(text='Бравлеры', callback_data=f'1 {player_tag}')],
        [InlineKeyboardButton(text='Клуб игрока', callback_data=f'2 {player_tag}')],
        [InlineKeyboardButton(text='Последние бои', callback_data=f'3 {player_tag}')]
    ]

    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(descr)
    photo = requests.get(f'https://cdn.brawlstats.com/player-thumbnails/{profile["icon"]["id"]}.png').content
    await update.message.chat.send_photo(photo, filename=profile['name'], reply_markup=markup)


async def handle(update: Update, context: CallbackContext):
    text = update.callback_query.data
    if text.startswith('1'):

        player_tag = text.split()[-1]
        profile = requests.get(
            f'https://api.brawlstars.com/v1/players/%23{player_tag}',
            headers={'Authorization': f'Bearer {bs_key}'}
        ).json()
        for brawler in profile['brawlers']:
            descr = f'{brawler["name"]}\n' + f"Сила: {brawler['power']}\nРанг: {brawler['rank']}\nТрофеев: {brawler['trophies']}"

            await update.callback_query.message.chat.send_message(descr)
            await update.callback_query.message.chat.send_photo(
                requests.get(f'https://cdn.brawlstats.com/character-arts/{brawler["id"]}.png').content
            )

    elif text.startswith('2'):

        player_tag = text.split()[-1]

        profile = requests.get(
            f'https://api.brawlstars.com/v1/players/%23{player_tag}',
            headers={'Authorization': f'Bearer {bs_key}'}
        ).json()

        club_ = requests.get(f'https://api.brawlstars.com/v1/clubs/%23{profile["club"]["tag"][1:]}',
                             headers={'Authorization': f'Bearer {bs_key}'}).json()

        members = '\n- '.join([f'{i["name"]} {i["tag"]} - {i["trophies"]} трофеев' for i in club_['members']])
        descr = (f"Тег: {club_['tag']}\nКол-во игроков: {len(club_['members'])}/30\n"
                 f"Трофеев: {club_['trophies']}\nОписание: {club_['description']}\n Участники:\n - {members}")
        descr = f'{club_["name"]}\n' + descr

        await update.callback_query.message.chat.send_message(descr)

    elif text.startswith('3'):
        player_tag = text.split()[-1]

        log = requests.get(
            f'https://api.brawlstars.com/v1/players/%23{player_tag}/battlelog',
            headers={'Authorization': f'Bearer {bs_key}'}
        ).json()

        msg = []
        for battle in log['items']:
            battle = battle['battle']
            if 'Showdown' not in battle['mode']:
                if battle['result'] == 'victory':
                    msg.append(f'✅ {battle["mode"]}: {battle["duration"]} seconds')
                else:
                    msg.append(f'❌ {battle["mode"]}: {battle["duration"]} seconds')
            elif battle['mode'] == 'soloShowdown':
                if battle['rank'] <= 4:
                    msg.append(f'✅ {battle["mode"]}: +{battle["trophyChange"]} trophies')
                else:
                    msg.append(f'❌ {battle["mode"]}: -{battle["trophyChange"]} trophies')
            else:
                if battle['rank'] <= 2:
                    msg.append(f'✅ {battle["mode"]}: +{battle["trophyChange"]} trophies')
                else:
                    msg.append(f'❌ {battle["mode"]}: -{battle["trophyChange"]} trophies')

        await update.callback_query.message.chat.send_message('\n'.join(msg))


application.add_handler(CommandHandler('info', info))
application.add_handler(CommandHandler('top', top))
application.add_handler(CallbackQueryHandler(handle))

application.run_polling(allowed_updates=Update.ALL_TYPES)
