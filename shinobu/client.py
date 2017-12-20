import discord
import yaml
import sys
import asyncio
from importlib import import_module, reload as reload_module
from .utilities import SHINOBU_FIRST_RUN_CONFIG, Logger
sys.path.append('./modules')

SUPPORTED_EVENTS = [
    'on_message',
    'on_ready'
]

def build_event_manager(event_name):
    async def shinobu_event_manager(*args, **kwargs):
        for handler in shinobu.events[event_name]:
            try:
                await handler(*args, **kwargs)
            except Exception as e:
                Logger.warn(f'SEM({event_name.upper()}) {type(e)}: {str(e)}')
    return shinobu_event_manager

class Shinobu(discord.Client):
    __instance__ = None
    events = {}
    commands = {}
    modules = {}

    def __new__(cls, *args, **kwargs):
        if not Shinobu.__instance__:
            self = super().__new__(cls)
            super(Shinobu, self).__init__()
            Shinobu.__instance__ = self
        return Shinobu.__instance__

    def __init__(self):
        pass

    def startup(self):
        config = self.load_config()
        for event_name in SUPPORTED_EVENTS:
            self.events[event_name] = []

            setattr(self, event_name, build_event_manager(event_name))


        import shinobu.commands
        import shinobu.events
        for module_name in config['startup_modules']:
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

    def load_module(self, module_name, hard_reload=True):
        if module_name in self.modules:
            active_module = self.modules[module_name]
            if hard_reload:
                if hasattr(active_module, 'on_module_unload'):
                    try:
                        active_module.on_module_unload()
                    except:
                        Logger.error()
                        return False
            try:
                active_module = reload_module(active_module)


            except Exception as e:
                Logger.info(f'Problem reloading module \'{module_name}\': {str(e)}')
                return False

        else: #  module not yet loaded
            try:
                active_module = import_module(module_name)
            except Exception as e:
                Logger.info(f'Problem loading module \'{module_name}\': {str(e)}')
                return False

        self.__modules[module_name] = active_module
        return True

    @staticmethod
    def command(invocation:str):
        def decorate(command_function):
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
            Logger.info('Added event')
        return handler


shinobu = Shinobu()


