import asyncio
from shinobu.command import *
import json
import traceback
from datetime import datetime
import shlex
import traceback



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
    def info(cls, message):
        time = datetime.now().strftime('%d %b %Y-%I:%M%p')
        cls.log(f"[{time}] (INFO): {message}", level='INFO')

    @classmethod
    def warn(cls, message):
        time = datetime.now().strftime('%d %b %Y-%I:%M%p')
        cls.log(f"[{time}] (WARN): {message}", level='WARN')

    class reporter:
        def __init__(self, limit=1):
            self.limit = 1

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, trace):
            if trace:
                tb_frames = traceback.extract_tb(trace, limit=3)
                frame = tb_frames.pop()
                Logger.error(f'{os.path.basename(frame[0])}, line {frame[1]} in {frame[2]}: {exc_type.__name__}: {str(exc_val)}')
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
    return shlex.split(message)


async def author_response():
    import inspect
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