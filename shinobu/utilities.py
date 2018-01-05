import asyncio
from shinobu.commands import *
import json
import traceback
from datetime import datetime
import shlex
import traceback
import inspect


import sys, os

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def alias(command, *variable_args, **long_args):
    @permissions("everyone")
    async def wrap(message, *args, **kwargs):
        arguments = variable_args
        arguments += args
        longargs = dict(**long_args)
        longargs.update(**kwargs)
        return await command(message, *arguments, **longargs)
    return wrap

class StopPropagation(Exception):
    __slots__ = []


class Logger:

    handlers = {
        'DEBUG':[eprint],
        'INFO' :[eprint],
        'WARN' :[eprint],
        'ERROR':[eprint]
    }

    @classmethod
    def log(cls, message:str, level="DEBUG"):
        if level in cls.handlers:
            for handler in cls.handlers[level]:
                try:
                    handler(message)
                except:
                    pass

    @classmethod
    def error(cls, message):
        time        = datetime.now().strftime('%d %b %Y-%I:%M%p')

        cls.log(f"[{time}] (ERROR) {message}", level='ERROR')

    @classmethod
    def debug(cls, message):
        pass

    @classmethod
    def info(cls, message):
        time = datetime.now().strftime('%d %b %Y-%I:%M%p')
        cls.log(f"[{time}] (INFO): {message}", level='INFO')

    @classmethod
    def warn(cls, message):
        time = datetime.now().strftime('%d %b %Y-%I:%M%p')
        cls.log(f"[{time}] (WARN): {message}", level='WARN')

    class reporter:
        def __init__(self, limit=5):
            self.limit = 5

        def __enter__(self, limit=5):
            self.limit = limit
            return self

        def __exit__(self, exc_type, exc_val, trace):
            if exc_type is StopPropagation:
                raise exc_val
            if trace:
                tb_frames = traceback.extract_tb(trace, self.limit)
                first = tb_frames.pop()
                Logger.error(f'{first[0]}, line {first[1]} in {first[2]}: {exc_type.__name__}: {str(exc_val)}')
                for frame in tb_frames:
                    print(f'\tline {frame[1]} in {frame[0]}')
                return True




SHINOBU_FIRST_RUN_CONFIG = """
discord:
  email: ''
  password: ''
  bot_token: ''

instance_name: Default

startup_modules:
  - core

database:
  type: sqlite
  name: shinobu.db
"""

def parse_args(message):
    try:
        args = shlex.split(message)
    except:
        args = message.split(' ')
    return args


async def author_response():

    from shinobu import shinobu
    frame = inspect.currentframe()
    try:
        locals = frame.f_back.f_locals
        author = locals['message'].author
        channel = locals['message'].channel
        message = await shinobu.wait_for_message(author=author, channel=channel)
        return message
    finally:
        del frame


def support_reloading(*modules):
    from importlib import reload
    for module in modules:
        reload(module)

def rtfembed(title, description, color, url=None):
    from discord import Embed
    embed = Embed(title=title, description=description, color=color, url=url)
    return embed