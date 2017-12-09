import asyncio
from shinobu.annotations import *
import json
import traceback
from datetime import datetime

import sys

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

DEBUG    = 10
INFO     = 20
ERROR    = 30

class ShinobuLog:

    handlers = []

    @classmethod
    def log(cls, message:str, level=INFO, *args, **kwargs):
        log_message = message.format(*args, **kwargs)
        for handler in cls.handlers:
            try:
                handler(log_message, level)
            except:
                pass

    @classmethod
    def error(cls, label=None):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        details = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__,
            'message': getattr(exc_value, 'message', ''),  # or see traceback._some_str()
        }
        del (exc_type, exc_value, exc_traceback)
        cls.log(
            "[{time}] ({label}:{function}:{lineno}) {type}:{msg}",
            time=datetime.now().strftime('%d %b %Y-%I:%M%p'),
            label=label or details['filename'],
            lineno=details['lineno'],
            function=details['name'],
            type=details['type'],
            msg=details['message']
        )

    @classmethod
    def info(cls, message, label=None):
        cls.log(
            "[{time}] ({label}): {msg}",
            time=datetime.now().strftime('%d %b %Y-%I:%M%p'),
            label=label or 'Shinobu',
            msg=message
        )

ShinobuLog.handlers.append(lambda msg, _: print(msg))


