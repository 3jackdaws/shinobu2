import asyncio
import sys
from importlib import import_module, reload as reload_module
from peewee import SqliteDatabase

import discord
import yaml

from .utilities import SHINOBU_FIRST_RUN_CONFIG, Logger, StopPropagation

sys.path.append('./modules')

SUPPORTED_EVENTS = [
    'on_message',
    'on_ready',
    'on_error',
    'on_reaction_add',
    'on_member_join',
    'on_member_remove'
]

def build_event_manager(event_name):
    async def shinobu_event_manager(*args, **kwargs):
        try:
            for handler in shinobu.events[event_name]:
                with Logger.reporter():
                    await handler(*args, **kwargs)
        except StopPropagation as e:
            print(e)

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
            with Logger.reporter():
                self.load_module(module_name)

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

        self.run(*login_credentials)

    def load_config(self):
        CONFIG_FILENAME = 'shinobu.yml'
        try:
            with open(CONFIG_FILENAME) as fp:
                config = yaml.safe_load(fp)
        except FileNotFoundError as e:
            Logger.warn(f'{CONFIG_FILENAME} not found.  Generating first run config file.')
            with open(CONFIG_FILENAME, "w") as fp:
                fp.write(SHINOBU_FIRST_RUN_CONFIG)
            raise SystemExit()
        return config

    def load_module(self, module_name):
        if module_name in self.modules:
            unloaded_module = self.unload_module(module_name)
            loaded_module = reload_module(unloaded_module)
        else:
            loaded_module = import_module(module_name)
        self.init_module(loaded_module)
        self.modules[module_name] = loaded_module
        events, commands = (
            len(getattr(loaded_module, "events", [])),
            len(getattr(loaded_module, "commands", [])),
        )
        Logger.info(f'Loaded module "{module_name}" with [{events}] events, [{commands}] commands.')

    def unload_module(self, module_name, hard=True):

        loaded_module = self.modules[module_name]

        if hard and hasattr(loaded_module, 'on_module_unload'):
            if asyncio.iscoroutinefunction(loaded_module.on_module_unload):
                self.invoke(loaded_module.on_module_unload())
            else:
                loaded_module.on_module_unload()

        if hasattr(loaded_module, 'commands'):
            for command in loaded_module.commands:
                if command.name in self.commands:
                    del self.commands[command.name]

        del self.modules[module_name]
        return loaded_module


    def init_module(self, loaded_module):
        if hasattr(loaded_module, "commands"):
            self.commands.update({c.name:c for c in loaded_module.commands})


        for new_event in getattr(loaded_module, 'events', ''):
            event_name = new_event.type
            if event_name in self.events:
                event_handler_list = self.events[event_name]  # type: list
                if new_event in event_handler_list:
                    event_handler_list.remove(new_event)
                self.events[new_event.type].append(new_event)


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
            new_handler_name = f'{handler.__module__}.{handler.__name__}'
            for existing_handler in Shinobu.events[handler.__name__]:
                existing_handler_name = f'{existing_handler.__module__}.{existing_handler.__name__}'
                if existing_handler_name == new_handler_name:
                    Shinobu.events[handler.__name__].remove(existing_handler)
            Shinobu.events[handler.__name__].append(handler)
        return handler



shinobu = Shinobu()


