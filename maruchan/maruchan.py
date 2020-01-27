"""Maru-chan."""
from discord.ext import commands
from marubot import MaruBot
import json
import codecs
import upsidedown
from rcon import RCON
import logging
import docker

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

bot = MaruBot(command_prefix=commands.when_mentioned)


@bot.event
async def on_ready():
    """on_ready."""
    logger.debug('Logged in as')
    logger.debug(bot.user.name)
    logger.debug(bot.user.id)
    logger.debug('------')


@bot.command()
async def say(*, what_to_say: str):
    """say."""
    logger.debug("say:" + what_to_say)
    await bot.say(what_to_say)


@bot.command()
async def unflip(*, what_to_unflip: str):
    """unflip."""
    logger.debug("unflip:" + what_to_unflip)
    if(what_to_unflip == "table"):
        await bot.say("┬─┬ノ(๑╹っ╹๑ノ)")
    else:
        await bot.say(what_to_unflip+"ノ(๑╹っ╹๑ノ)")


@bot.command()
async def flip(*, what_to_flip: str):
    """flip."""
    logger.debug("flip:" + what_to_flip)
    if(what_to_flip == "table"):
        await bot.say("(╯✿ㆁᴗㆁ）╯︵ ┻━┻")
    else:
        await bot.say("(╯✿ㆁᴗㆁ）╯︵" + upsidedown.transform(what_to_flip))


@bot.command()
async def starbound_players():
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
        await bot.say("(－ω－) zzZ")
        return
    if players.startswith("There are 0/"):
        await bot.say("(◞ ‸ ◟✿) no hay nadie jugando")
    else:
        await bot.say("(✿•̀ ▽ •́ )φ:\n" + players)


bot.run(config["bot"]["token"])
