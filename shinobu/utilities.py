import asyncio
from shinobu.annotations import *
import json
import traceback
from datetime import datetime

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

class ShinobuConfig(dict):
    __master__ = {}
    config_file = None
    def __init__(self, group=None):
        self.group = group
        if group:
            if group not in ShinobuConfig.__master__:
                ShinobuConfig.__master__[group] = {}
            config = ShinobuConfig.__master__.get(group, {}).copy()
        else:
            config = ShinobuConfig.__master__.copy()
            super(ShinobuConfig, self).__init__(**config)

    @classmethod
    def load(cls, config_file_path):
        if not cls.config_file:
            cls.config_file = config_file_path
        try:
            with open(config_file_path) as fp:
                config = json.load(fp)
                cls.__master__.clear()
                cls.__master__.update(config)
                cls.config_file = config_file_path
                return True

        except json.JSONDecodeError as j:
            eprint(j)
        except Exception as e:
            eprint('Problem loading config: {}'.format(str(e)))
        return False

    @classmethod
    def reload(cls):
        cls.load(cls.config_file)

    @classmethod
    def write_file(cls):
        with open(cls.config_file, 'w+') as fp:
            fp.write(cls)

    def save(self):
        if self.group:
            ShinobuConfig.__master__[self.group] = dict(self)
        else:
            ShinobuConfig.__master__ = dict(self)
        with open(self.config_file, 'w+') as fp:
            json.dump(self, fp, indent=2)


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
    def error(cls):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        details = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__,
            'message': str(exc_value)
        }
        del (exc_type, exc_value, exc_traceback)

        time        = datetime.now().strftime('%d %b %Y-%I:%M%p')
        filename    = details['filename']
        lineno      = details['lineno']
        function    = details['name']
        type        = details['type']
        msg         = details['message']
        cls.log(f"[{time}] (ERROR) in {os.path.basename(filename)}:{function}:{lineno} {type}: {msg}", level='ERROR')

    @classmethod
    def info(cls, message):
        time = datetime.now().strftime('%d %b %Y-%I:%M%p')
        cls.log(f"[{time}] (INFO): {message}", level='INFO')

    @classmethod
    def warn(cls, message):
        time = datetime.now().strftime('%d %b %Y-%I:%M%p')
        cls.log(f"[{time}] (WARNING): {message}", level='WARN')


SHINOBU_FIRST_RUN_CONFIG = """
discord:
  email: ''
  password: ''
  bot_token: ''

instance_name: Default

startup_modules:
  - base

database:
  type: sqlite
  name: shinobu.db
"""

