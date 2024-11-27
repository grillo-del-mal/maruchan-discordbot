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
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    await bot.add_cog(TableFlip(bot))
    await bot.add_cog(Starbound(bot, config['starbound']))
    logger.info('------')

installed = False

@bot.command()
async def install(ctx: commands.Context):
    global installed
    if installed:
        return

    if config["bot"]["admin"] != ctx.message.author.id:
        logger.error('Unknown id: %d' % ctx.message.author.id)
        return

    await bot.add_cog(MaruAI(bot, ctx.message.channel, config['maruai']))
    installed = True

@bot.command()
async def uninstall(ctx: commands.Context):
    global installed
    if not installed:
        return

    if config["bot"]["admin"] != ctx.message.author.id:
        logger.error('Unknown id: %d' % ctx.message.author.id)
        return

    await bot.remove_cog("MaruAI")
    installed = False

bot.run(config["bot"]["token"])
