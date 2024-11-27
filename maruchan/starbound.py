from discord.ext import commands
import logging

from rcon import RCON

logger = logging.getLogger("root")

class Starbound(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @commands.command()
    async def starbound_players(self, ctx: commands.Context):
        u"""starbound_players.

        Dice que jugadores estan en el servidor ahora.
        """
        players = ""
        try:
            rcon = RCON(
                self.config["hostname"],
                self.config["port"],
                self.config["rcon_password"])
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
