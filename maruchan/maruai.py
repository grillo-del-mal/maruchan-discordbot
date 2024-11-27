from discord.ext import tasks, commands
from copy import deepcopy
import requests
import logging
import json
import codecs
import random
import re
import time
import typing
import functools
import typing
import asyncio

logger = logging.getLogger("root")

DEFAULT_QUERY = {
    "stream": False,
    "n_predict": 400,
    "temperature": 0.7,
    "stop": [
        "</s>",
        "Maru-chan:",
        "Term:",
        "term:",
    ],
    "repeat_last_n": 256,
    "repeat_penalty": 1.18,
    "penalize_nl": False,
    "dry_multiplier": 0,
    "dry_base": 1.75,
    "dry_allowed_length": 2,
    "dry_penalty_last_n": -1,
    "top_k": 40,
    "top_p": 0.95,
    "min_p": 0.05,
    "xtc_probability": 0,
    "xtc_threshold": 0.1,
    "typical_p": 1,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "mirostat": 0,
    "mirostat_tau": 5,
    "mirostat_eta": 0.1,
    "grammar": "",
    "n_probs": 0,
    "min_keep": 0,
    "image_data": [],
    "cache_prompt": True,
    "api_key": "",
    "prompt": ""
}

BASE_PROMPT = """Esta es la interacción entre Term y Maru-chan
Maru-chan es una Chilena joven que le gusta ayudar a la gente en el chat y le gusta mucho el Ramen.
Maru-chan es modesta, humilde, escribe con buena gramática.
Maru-chan no comparte información personal y no responde en más de 30 palabras.
Term es la terminal con la que Maru-chan interactúa para hablar con el chat.
Maru-chan escribe en Term solo lo necesario para cumplir con los requerimientos de Term.

"""

EMO_PROMPT = """Maru-chan es una Chilena joven que le gusta ayudar a la gente en el chat.
Maru-chan es modesta, humilde, escribe con buena gramática.
Maru-chan solo puede describir usando palabras de la siguiente lista: %s

"""

HEADERS = {'Content-type': 'application/json', 'Accept': 'application/json'}

fp = codecs.open("emotes/kaomoji.json", "r", "utf-8")
data = fp.read()
kaomoji = json.loads(data)
fp.close()

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

class MaruAI(commands.Cog):

    def __init__(self, bot, channel, config):
        self.bot = bot
        self.channel = channel
        self.config = config
        self.chat_history = []
        self.new_msgs = 0
        logger.info(BASE_PROMPT)

        self.general_chat.start()

    def cog_unload(self):
        self.general_chat.cancel()

    def clean_message(self, message):
        response = message.content.strip().split('\n')[0]
        for stop in DEFAULT_QUERY['stop']:
            response = response.replace(stop, '')
        users = {men.id: men.display_name for men in message.mentions}
        for id, display in users.items():
            response = response.replace("<@%d>" % id, display)
        return response

    def write_history(self,n):
        return [
            "Term: %s escribió: '%s'" % (usr.display_name, msg)
            if usr != self.bot.user else
            "Maru-chan: %s" % msg
            for (_, usr, msg) in self.chat_history ][-n:]

    @to_thread
    def check_answer(self):
        query = deepcopy(DEFAULT_QUERY)
        query['prompt'] = "\n".join([
            BASE_PROMPT,
            *self.write_history(18),
            "Term: Responde en una oracion de menos de 30 palabras."
            if len(self.chat_history) > 0 else
            "Term: El chat está encendido, presentate en menos de 30 palabras.",
            "Maru-chan: "])
        r = requests.post(self.config["hostname"] + '/completion', json=query, headers=HEADERS)
        return r.json()["content"].strip().split('\n')[0].strip()

    @to_thread
    def check_emo(self, msg):
        query = deepcopy(DEFAULT_QUERY)
        query['prompt'] = "\n".join([
            EMO_PROMPT % (", ".join(kaomoji.keys())),
            "Term: Considerando la siguiente conversación:",
            *self.write_history(18),
            "Maru-chan: %s" % msg,
            "",
            "Term: Que emocion de la lista sientes cuando dices la ultma frase? Responde en una palabra.",
            "Maru-chan: "])
        r = requests.post(self.config["hostname"] + '/completion', json=query, headers=HEADERS)
        maru_resp = r.json()["content"].strip().split('\n')[0].strip().lower()
        logger.info(maru_resp)
        rr = re.search(r'[a-z]+', maru_resp)
        maru_resp = rr[0] if rr is not None else ''

        kao = '(✿ㆁᴗㆁ)'
        if maru_resp in kaomoji:
            kao = random.sample(kaomoji[maru_resp], 1)[0]
        return kao
    
    def append_history(self, author, message):
        self.chat_history.append((time.time(), author, message))

    async def send_msg(self):
        self.new_msgs = 0

        maru_resp = await self.check_answer()
        emo = await self.check_emo(maru_resp)

        logger.info("Maru-chan: %s %s" % (emo, maru_resp))

        self.append_history(self.bot.user, maru_resp)
        await self.channel.send("%s %s" % (emo, maru_resp))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.channel != self.channel:
            return

        msg_text = self.clean_message(message)
        self.append_history(message.author, msg_text)
        logger.info("Term: %s escribió: '%s'" % (message.author.display_name, msg_text))
        self.new_msgs += 1

        # Respond inmediately
        if self.bot.user in message.mentions:
            await self.send_msg()

    @tasks.loop(seconds=15.0)
    async def general_chat(self):
        if self.new_msgs == 0 and len(self.chat_history) > 0:
            return
        
        # Clear outdated messages
        cut_time = time.time() - 1800
        while len(self.chat_history) > 0 and self.chat_history[0][0] < cut_time:
            logger.debug("Msg timeout")
            self.chat_history.pop(0)

        await self.send_msg()
