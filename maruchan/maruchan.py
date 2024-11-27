"""Maru-chan."""
import discord
from discord.ext import commands
from discord.ext.commands.view import StringView
import json
import codecs
import logging

from tableflip import TableFlip
from starbound import Starbound
from maruai import MaruAI

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

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

@bot.event
async def on_ready():
    """on_ready."""
    logger.debug('Logged in as')
    logger.debug(bot.user.name)
    logger.debug(bot.user.id)
    await bot.add_cog(TableFlip(bot))
    await bot.add_cog(Starbound(bot, config['starbound']))
    logger.debug('------')

installed = False

@bot.command()
async def install(ctx: commands.Context):
    if config["bot"]["admin"] == ctx.message.author.id:
        return

    if installed:
        return
    await bot.add_cog(MaruAI(bot, ctx.message.channel, config['maruai']))
    installed = True

@bot.command()
async def uninstall(ctx: commands.Context):
    if config["bot"]["admin"] == ctx.message.author.id:
        return

    if not installed:
        return
    await bot.remove_cog("MaruAI")
    installed = False

bot.run(config["bot"]["token"])
