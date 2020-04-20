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
from pymongo import MongoClient

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

client = MongoClient(
    'mongo',
    username='root',
    password='password')

db = client.get_database("animal_crossing")

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

        prefixes = await bot.get_prefix(message)
        start = view.get_word() 
        logger.debug("checking if " + str(start) + " in " + str(prefixes))
        
        # Revisar 
        if len(list(
            filter(
                lambda x: x is True,
                [start == prefix[:-1] for prefix in prefixes]
                ))) == 0:
            return

        view.skip_ws()
        key = None
        if not view.eof:
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

@bot.command()
async def AC(ctx: commands.Context, *, stock_command: str):
    """Animal Crossing."""
    logger.debug("AC:" + stock_command)
    logger.debug("  author: " + str(ctx.author))
    logger.debug("  channel: " + str(ctx.channel))
    logger.debug("  guild: " + str(ctx.guild))
    logger.debug("  me: " + str(ctx.me))

    command = []
    view = StringView(stock_command)
    i = 0
    while not view.eof:
        arg = view.get_word()
        logger.debug("   arg[" + str(i) + "]: " + arg)
        command.append(arg)
        view.skip_ws()
        i += 1

    member_name = str(ctx.author.name) + "#" + str(ctx.author.discriminator)

    db["stalk_market"].insert_one({
        "user": member_name,
        "command": command
    })

bot.run(config["bot"]["token"])
