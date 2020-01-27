"""MaruBot."""

from discord.ext import commands
from discord.ext.commands.view import StringView
import codecs
import json
import random
import discord

fp = codecs.open("emotes/kaomoji.json", "r", "utf-8")
data = fp.read()
kaomoji = json.loads(data)
fp.close()

class MaruBot(commands.Bot):
    """MaruBot."""

    async def on_message(self, message:discord.Message):
        """on_message."""
        ctx = await self.get_context(message)

        if ctx.command is None:
            print("kao")
            # Invocar Kaomojis si existen
            key = invoker
            if key not in kaomoji.keys():
                key = random.sample(kaomoji.keys(), 1)[0]
            kao = random.sample(kaomoji[key], 1)[0]
            print(kao)
            await message.channel.send(kao)
        else:
            print("processing")
            self.process_commands(message)
