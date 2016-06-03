import random
import json
import codecs

fp = codecs.open("emotes/kaomoji.json", "r", "utf-8")
data = fp.read()
kaomoji = json.loads(data)
fp.close()

fp = codecs.open("config.json", "r")
data = fp.read()
config = json.loads(data)
fp.close()

from discord.ext import commands
from discord.message import Message

from discord.ext.commands.core import GroupMixin, Command, command
from discord.ext.commands.view import StringView
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandNotFound
from discord.ext.commands.formatter import HelpFormatter

import asyncio

class TokenBot(commands.Bot):
    '''
    def run(self, token):
        self.token = token
        self.headers['authorization'] = token
        self._is_logged_in.set()
        try:
            self.loop.run_until_complete(self.connect())
        except:
            self.loop.run_until_complete(self.logout())
            pending = asyncio.Task.all_tasks()
            gathered = asyncio.gather(*pending)
            try:
                gathered.cancel()
                self.loop.run_forever()
                gathered.exception()
            except:
                pass
        finally:
            self.loop.close()
    '''         
            
    @asyncio.coroutine
    def process_commands(self, message):

        _internal_channel = message.channel
        _internal_author = message.author

        view = StringView(message.content)
        if message.author == self.user:
            return

        prefix = self._get_prefix(message)
        invoked_prefix = prefix
        
        if not isinstance(prefix, (tuple, list)):
            if not view.skip_string(prefix):
                
                ## procesar emoticons
                yield from self.process_emotes(message, view)
                return
        else:
            invoked_prefix = discord.utils.find(view.skip_string, prefix)
            if invoked_prefix is None:
                return

        invoker = view.get_word()
        tmp = {
            'bot': self,
            'invoked_with': invoker,
            'message': message,
            'view': view,
            'prefix': invoked_prefix
        }
        ctx = Context(**tmp)
        del tmp

        if invoker in self.commands:
            command = self.commands[invoker]
            self.dispatch('command', command, ctx)
            ctx.command = command
            yield from command.invoke(ctx)
            self.dispatch('command_completion', command, ctx)
        else:
            exc = CommandNotFound('Command "{}" is not found'.format(invoker))
            self.dispatch('command_error', exc, ctx)

            ## Invocar Kaomojis si existen
            key = invoker
            if(key not in kaomoji.keys()):
                key = random.sample(kaomoji.keys(), 1)[0]
            kao = random.sample(kaomoji[key],1)[0]
            yield from self.say(kao)
            
    @asyncio.coroutine
    def process_emotes(self, message: Message, view):
        tmp = {
            'bot': self,
            'invoked_with': '',
            'message': message,
            'view': view,
            'prefix': ''
        }
        ctx = Context(**tmp)
        del tmp


            
bot = TokenBot(command_prefix=commands.when_mentioned)

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
@asyncio.coroutine
def say(*, what_to_say : str):
    print("say:" + what_to_say)
    yield from bot.say(what_to_say)

@bot.command()
@asyncio.coroutine
def unflip(*, what_to_unflip : str):
    print("unflip:" + what_to_unflip)
    if(what_to_unflip == "table"):
        yield from bot.say("┬─┬ノ(๑╹っ╹๑ノ)")
    else:
        yield from bot.say(what_to_unflip+"ノ(๑╹っ╹๑ノ)")

        
import upsidedown

@bot.command()
@asyncio.coroutine
def flip(*, what_to_flip):
    print("flip:" + what_to_flip)
    if(what_to_flip == "table" ):
        yield from bot.say("(╯✿ㆁᴗㆁ）╯︵ ┻━┻")
    else:
        yield from bot.say("(╯✿ㆁᴗㆁ）╯︵" + upsidedown.transform(what_to_flip) )

bot.run(config["bot"]["token"])


