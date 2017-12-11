import discord
import yaml
import sys
from importlib import import_module, reload as reload_module
from .utilities import SHINOBU_FIRST_RUN_CONFIG, Logger
sys.path.append('./modules')

EVENTS = [
    'on_message',
    'on_ready'
]

class Shinobu(discord.Client):
    __instance__ = None
    __events = {}
    __commands = {}
    __modules = {}

    def __init__(self):
        if not self.__instance__:
            self.__instance__ = self
            super(Shinobu, self).__init__()
        self.__dict__ = self.__instance__.__dict__

    def startup(self):
        config = self.load_config()
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
        if module_name in self.__modules:
            active_module = self.__modules[module_name]
            if hard_reload:
                if hasattr(active_module, 'on_module_unload'):
                    try:
                        active_module.on_module_unload()
                    except:
                        Logger.error()
            try:
                active_module = reload_module(active_module)
            except Exception as e:
                Logger.info(f'Problem reloading module \'{module_name}\': {str(e)}')
            self.__modules[module_name] = active_module

        else: #  module not yet loaded
            try:
                active_module = import_module(module_name)
            except Exception as e:
                Logger.info(f'Problem loading module \'{module_name}\': {str(e)}')




