from discord.ext import commands
import logging

import upsidedown

logger = logging.getLogger("root")

class TableFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_users(self, message, mentions):
        users = {men.id: men.display_name for men in mentions}
        for id, display in users.items():
            message = message.replace("<@%d>"%id, display)
        return message

    @commands.command()
    async def unflip(self, ctx: commands.Context, *, what_to_unflip: str='table'):
        """unflip."""
        what_to_unflip = self.check_users(what_to_unflip, ctx.message.mentions)
        logger.debug("unflip:" + what_to_unflip)
        if(what_to_unflip == "table"):
            await ctx.send("┬─┬ノ(๑╹っ╹๑ノ)")
        else:
            await ctx.send(what_to_unflip+"ノ(๑╹っ╹๑ノ)")

    @commands.command()
    async def flip(self, ctx: commands.Context, *, what_to_flip: str='table'):
        """flip."""
        what_to_flip = self.check_users(what_to_flip, ctx.message.mentions)
        logger.debug("flip:" + what_to_flip)
        if(what_to_flip == "table"):
            await ctx.send("(╯✿ㆁᴗㆁ）╯︵ ┻━┻")
        else:
            await ctx.send("(╯✿ㆁᴗㆁ）╯︵" + upsidedown.transform(what_to_flip))
