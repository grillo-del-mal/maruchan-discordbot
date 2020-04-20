"""Maru-chan."""
import discord
from discord.ext import commands
from discord.ext.commands.view import StringView
import json
import codecs
import upsidedown
import random
from rcon import RCON
import logging

formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

shandler = logging.StreamHandler()
shandler.setFormatter(formatter)

logger = logging.getLogger("root")
logger.setLevel(getattr(logging, 'DEBUG'))
logger.addHandler(shandler)

fp = codecs.open("/data/config.json", "r")
data = fp.read()
config = json.loads(data)
fp.close()

fp = codecs.open("emotes/kaomoji.json", "r", "utf-8")
data = fp.read()
kaomoji = json.loads(data)
fp.close()

bot = commands.Bot(command_prefix=commands.when_mentioned)

@bot.event
async def on_ready():
    """on_ready."""
    logger.debug('Logged in as')
    logger.debug(bot.user.name)
    logger.debug(bot.user.id)
    logger.debug('------')

@bot.event
async def on_message(message:discord.Message):
    """on_message."""
    ctx = await bot.get_context(message)

    if ctx.command is None:
        if message.author.bot:
            return

        logger.debug("kao")
        # Invocar Kaomojis si existen
        view = StringView(message.content)

        prefix = await bot.get_prefix(message)
        start = view.get_word()
        logger.debug("checking if " + str(start) + " in " + str(prefix))
        if start not in prefix:
            return

            key = view.get_word()

        logger.debug("checking " + str(key))
        if key not in kaomoji.keys():
            key = random.sample(kaomoji.keys(), 1)[0]

        kao = random.sample(kaomoji[key], 1)[0]
        logger.debug(kao)
        await ctx.channel.send(kao)
    else:
        logger.debug("processing")
        await bot.process_commands(message)

@bot.command()
async def say(ctx: commands.Context, *, what_to_say: str):
    """say."""
    logger.debug("say:" + what_to_say)
    await ctx.send(what_to_say)

@bot.command()
async def unflip(ctx: commands.Context, *, what_to_unflip: str):
    """unflip."""
    logger.debug("unflip:" + what_to_unflip)
    if(what_to_unflip == "table"):
        await ctx.send("┬─┬ノ(๑╹っ╹๑ノ)")
    else:
        await ctx.send(what_to_unflip+"ノ(๑╹っ╹๑ノ)")

@bot.command()
async def flip(ctx: commands.Context, *, what_to_flip: str):
    """flip."""
    logger.debug("flip:" + what_to_flip)
    if(what_to_flip == "table"):
        await ctx.send("(╯✿ㆁᴗㆁ）╯︵ ┻━┻")
    else:
        await ctx.send("(╯✿ㆁᴗㆁ）╯︵" + upsidedown.transform(what_to_flip))

@bot.command()
async def starbound_players(ctx: commands.Context):
    u"""starbound_players.

    Dice que jugadores estan en el servidor ahora.
    """
    players = ""
    try:
        rcon = RCON(
            config["starbound"]["hostname"],
            config["starbound"]["port"],
            config["starbound"]["rcon_password"])
        rcon.connect()
        rcon.auth()
        players = str(rcon.send_msg("list")[2])[2:-1]
        rcon.disconnect()
    except Exception as e:
        logger.error(
            "starbound_players():" + str(e),
            exc_info=True)
        await ctx.send("(－ω－) zzZ")
        return
    if players.startswith("There are 0/"):
        await ctx.send("(◞ ‸ ◟✿) no hay nadie jugando")
    else:
        await ctx.send("(✿•̀ ▽ •́ )φ:\n" + players)


bot.run(config["bot"]["token"])
