from credits import ds_token as bot_token
import discord
from discord.ext import commands
from credits import bs_key
import requests

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix='/')


# hex to rgb
def hex_to_rgb(h: str) -> [int, int, int]:
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# Отображает основную информацию об аккаунте
@bot.command(name='info')
async def info(ctx: commands.Context, player_tag: str):
    profile = requests.get(
        f'https://api.brawlstars.com/v1/players/%23{player_tag}',
        headers={'Authorization': f'Bearer {bs_key}'}
    ).json()

    descr = (f"Тег: {profile['tag']}\nТрофеев: {profile['trophies']}\n"
             f"Побед всего: {profile['3vs3Victories'] + profile['soloVictories'] + profile['duoVictories']}\n"
             f" - Сольные победы: {profile['soloVictories']}\n- Парные победы: {profile['duoVictories']}\n"
             f"- Командные победы: {profile['3vs3Victories']}")

    r, g, b = hex_to_rgb(profile['nameColor'][4:])

    embed_profile = discord.Embed(
        color=discord.Colour.from_rgb(r, g, b),
        title=profile['name'],
        description=descr,
    )
    embed_profile.set_thumbnail(url=f'https://cdn.brawlstats.com/player-thumbnails/{profile["icon"]["id"]}.png')

    await ctx.send(embed=embed_profile)


# Отображает всех бравлеров на аккаунте
@bot.command(name='brawlers')
async def brawlers(ctx: commands.Context, player_tag: str):
    profile = requests.get(
        f'https://api.brawlstars.com/v1/players/%23{player_tag}',
        headers={'Authorization': f'Bearer {bs_key}'}
    ).json()

    for brawler in profile['brawlers']:
        t = brawler['rank']

        if t < 5:
            r1, g1, b1 = hex_to_rgb('D75705')
        elif t < 10:
            r1, g1, b1 = hex_to_rgb('8188D1')
        elif t < 15:
            r1, g1, b1 = hex_to_rgb('ED9524')
        elif t < 20:
            r1, g1, b1 = hex_to_rgb('04AFF0')
        elif t < 25:
            r1, g1, b1 = hex_to_rgb('CA35FA')
        elif t < 30:
            r1, g1, b1 = hex_to_rgb('04BF6D')
        elif t < 35:
            r1, g1, b1 = hex_to_rgb('D4153C')
        else:
            r1, g1, b1 = hex_to_rgb('3A287B')

        descr = f"Сила: {brawler['power']}\nРанг: {brawler['rank']}\nТрофеев: {brawler['trophies']}"

        embed_brawler = discord.Embed(
            colour=discord.Colour.from_rgb(r1, g1, b1),
            title=brawler['name'],
            description=descr
        )
        embed_brawler.set_thumbnail(url=f'https://cdn.brawlstats.com/character-arts/{brawler["id"]}.png')
        await ctx.send(embed=embed_brawler)


# Информация о клубе из тега игрока
@bot.command(name='club')
async def club(ctx, player_tag):
    profile = requests.get(
        f'https://api.brawlstars.com/v1/players/%23{player_tag}',
        headers={'Authorization': f'Bearer {bs_key}'}
    ).json()

    club_ = requests.get(f'https://api.brawlstars.com/v1/clubs/%23{profile["club"]["tag"][1:]}',
                         headers={'Authorization': f'Bearer {bs_key}'}).json()

    members = '\n- '.join([f'{i["name"]} {i["tag"]} - {i["trophies"]} трофеев' for i in club_['members']])
    descr = (f"Тег: {club_['tag']}\nКол-во игроков: {len(club_['members'])}/30\n"
             f"Трофеев: {club_['trophies']}\nОписание: {club_['description']}\n Участники:\n - {members}")

    r, g, b = hex_to_rgb(profile['nameColor'][4:])

    embed_club = discord.Embed(
        color=discord.Colour.from_rgb(r, g, b),
        title=club_['name'],
        description=descr
    )

    await ctx.send(embed=embed_club)


# Глобальный топ игроков
@bot.command(name='top')
async def top(ctx, limit):
    top_ = requests.get(
        f'https://api.brawlstars.com/v1/rankings/global/players',
        headers={'Authorization': f'Bearer {bs_key}'}
    ).json()
    players = [i for i in top_['items'] if i['rank'] <= int(limit)]
    r, g, b = hex_to_rgb(players[0]['nameColor'][4:])
    descr = "\n- ".join([i['name'] for i in players])
    await ctx.send(embed=discord.Embed(
        title=f'Топ-{limit} игроков',
        description=f' - {descr}',
        color=discord.Colour.from_rgb(r, g, b)
    ))

bot.run(bot_token)
