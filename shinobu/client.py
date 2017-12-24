import asyncio
import sys
from importlib import import_module, reload as reload_module
from peewee import SqliteDatabase

import discord
import yaml

from .utilities import SHINOBU_FIRST_RUN_CONFIG, Logger

sys.path.append('./modules')

SUPPORTED_EVENTS = [
    'on_message',
    'on_ready',
    'on_error'
]

def build_event_manager(event_name):
    async def shinobu_event_manager(*args, **kwargs):
        for handler in shinobu.events[event_name]:
            with Logger.reporter():
                await handler(*args, **kwargs)

    return shinobu_event_manager

class Shinobu(discord.Client):
    __instance__ = None
    events = {}
    commands = {}
    modules = {}
    db = SqliteDatabase('shinobu.db')
    version = '2.5.2'


    def __new__(cls, *args, **kwargs):
        if not Shinobu.__instance__:
            self = super().__new__(cls)
            super(Shinobu, self).__init__()
            Shinobu.__instance__ = self
        return Shinobu.__instance__

    def __init__(self):
        pass

    def startup(self):
        self.db.connect()
        config = self.load_config()
        self.config = config
        self.name = config['instance_name']
        for event_name in SUPPORTED_EVENTS:
            self.events[event_name] = []

            setattr(self, event_name, build_event_manager(event_name))

        for module_name in config['startup_modules']:
            try:
                self.load_module(module_name)
            except Exception as e:
                Logger.error(e)

        login_credentials = []
        email = config['discord']['email']
        password = config['discord']['password']
        token = config['discord']['bot_token']
        if email and password:
            login_credentials = [email, password]
        elif token:
            login_credentials = [token]
        else:
            Logger.warn('No email and password or bot_token set in config.  Exiting...')
            exit()
        self.run(*login_credentials)

    def load_config(self):
        CONFIG_FILENAME = 'shinobu.yml'
        try:
            with open(CONFIG_FILENAME) as fp:
                config = yaml.safe_load(fp)
        except FileNotFoundError as e:
            Logger.warn(f'{CONFIG_FILENAME} not found.  Generating template config file.')
            with open(CONFIG_FILENAME, "w") as fp:
                fp.write(SHINOBU_FIRST_RUN_CONFIG)
            raise SystemExit()
        return config

    def load_module(self, module_name):
        if module_name not in self.modules:
            events, commands = (self.num_events(), self.num_commands(),)
            active_module = import_module(module_name)
            events = self.num_events() - events
            commands = self.num_commands() - commands
            self.modules[module_name] = active_module
            Logger.info(f'Loaded module "{module_name}" with [{events}] events, [{commands}] commands.')
            return True
        else:
            return False

    def unload_module(self, module_name, hard=True):
        if module_name not in self.modules:
            raise ModuleNotFoundError()

        module = self.modules[module_name]

        if hard and hasattr(module, 'on_module_unload'):
            if asyncio.iscoroutinefunction(module.on_module_unload):
                self.invoke(module.on_module_unload())
            else:
                module.on_module_unload()

        del self.modules[module_name]

    def reload_module(self, module_name, hard=True):
        if module_name not in self.modules:
            raise ModuleNotFoundError()
        active_module = self.modules[module_name]
        if hard and hasattr(active_module, 'on_module_unload'):
            if asyncio.iscoroutinefunction(active_module.on_module_unload):
                self.invoke(active_module.on_module_unload())
            else:
                active_module.on_module_unload()
        reload_module(self.modules[module_name])

    def invoke(self, coro):
        try:
            asyncio.ensure_future(coro, loop=self.loop)
            return True
        except:
            return False

    def num_commands(self):
        num = 0
        return len(self.commands)

    def num_events(self):
        num = 0
        for en, el in self.events.items():
            num += len(el)
        return num

    @staticmethod
    def command(invocation:str):
        def decorate(command_function):
            command_function.invocation = invocation
            Shinobu.commands[invocation] = command_function
            return command_function
        return decorate


    def event(self, handler):
        if not asyncio.iscoroutinefunction(handler):
            Logger.warn(f'Event "{handler.__name__}" from module "{handler.__module__}" is not a coroutine.')
        elif handler.__name__ not in Shinobu.events:
            Logger.warn(f'Module "{handler.__module__}" tried to register invalid event: "{handler.__name__}"')
        else:
            Shinobu.events[handler.__name__].append(handler)
        return handler



shinobu = Shinobu()


