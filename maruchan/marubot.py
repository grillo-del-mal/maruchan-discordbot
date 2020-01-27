"""MaruBot."""

from discord.ext import commands
from discord.ext.commands.view import StringView
import asyncio
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

    @asyncio.coroutine
    def on_message(self, message):
        """on_message."""
        view = StringView(message.content)
        prefix = yield from self._get_prefix(message)
        invoked_prefix = prefix

        if not isinstance(prefix, (tuple, list)):
            if not view.skip_string(prefix):
                return
        else:
            invoked_prefix = discord.utils.find(view.skip_string, prefix)
            if invoked_prefix is None:
                return

        invoker = view.get_word()
        print(invoker, self.commands)

        if invoker not in self.commands:
            print("kao")
            # Invocar Kaomojis si existen
            key = invoker
            if(key not in kaomoji.keys()):
                key = random.sample(kaomoji.keys(), 1)[0]
            kao = random.sample(kaomoji[key], 1)[0]
            print(kao)
            yield from self.send_message(message.channel, kao)
        else:
            print("processing")
            yield from self.process_commands(message)
