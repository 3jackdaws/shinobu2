
import discord
import asyncio
from discord import Message, User, Channel, Member, Role
import json
import asyncio
import os
from importlib import reload
import sys
import datetime
import getopt
import shlex
import traceback
from .utilities import ShinobuConfig, eprint, ShinobuLog
sys.path.append("modules")

__all__ = [
    "ShinobuClient",
    "Message"
]



SUPPORTED_EVENTS = [
    'on_message',
    'on_voice_state_update',

]


class ShinobuClient(discord.Client):
    owners = []
    log_channel = None
    events = {}
    commands = {}
    modules = {}

    def __init__(self, config_file):

        self.working_dir = os.path.dirname(config_file)

        super(ShinobuClient, self).__init__()
        self.__bootstrap__(config_file)

    def invoke(self, coroutine):
        asyncio.ensure_future(coroutine, loop=self.loop)

    def __bootstrap__(self, config_file):
        print("BOOTSTRAPPING")
        if not ShinobuConfig.load(config_file):
            self.config = ShinobuConfig()
            self.config.clear()
            self.config.update({
                "discord":{
                    "email":"",
                    "password":"",
                    "token":""
                },
                "owners":["owner id"],
                "instance_name":"Default"
            })
            self.config.save()
        else:
            self.config = ShinobuConfig()



        log_directory = self.working_dir + '/logs'
        if not os.path.exists(log_directory):
            os.mkdir(log_directory)

        log_chan_id = self.config.get('log_channel')
        self.log_channel = self.get_channel(log_chan_id) if log_chan_id else None

        self.log_file = open(log_directory + "/shinobu.log", "a+")

        def build_handler(event_name):
            async def event_manager(*args, **kwargs):
                print('EM:', event_name)
                for handler in self.events[event_name]:
                    try:
                        await handler(*args, **kwargs)
                    except Exception as e:
                        ShinobuLog.error()

            setattr(self, event_name, event_manager)
            self.events[event_name] = []

        for event in SUPPORTED_EVENTS:
            build_handler(event)



        # self.event(self.on_error)

    def can_execute(self, command_function, user:Member):
        if hasattr(command_function, "permissions"):

            if "everyone" in command_function.permissions:
                return True
            for role in user.roles:

                if role.name in command_function.permissions:
                    return True
        else:
            return user in self.owners

    def register_event(self, event_string, handler):
        if not asyncio.iscoroutinefunction(handler):
            raise Exception('not a coroutine')
        if event_string in self.events:
            self.events[event_string].append(handler)
            return True
        return False

    def register_command(self, command_name, handler):
        self.commands[command_name] = handler
        self.reg_cmd_num += 1
        return True




    def load_config_file(self, name, default={}):
        base = os.path.dirname(self.config_file)
        file = open(base + "/" + name + ".json", "a+")
        file.seek(0)
        config = default
        try:
            config = json.load(file)
        except:
            file.seek(0)
            json.dump(config, file)
        file.close()
        return config


    def write_config_file(self, name, obj):
        base = os.path.dirname(self.config_file)
        file = open(base + "/" + name + ".json", "w+")
        json.dump(obj, file, indent=2)
        file.close()


    def load_module(self, name, soft_reload=False):
        self.reg_cmd_num = 0
        events_before = len(self.events.values())
        try:
            if name in self.modules:
                if not soft_reload and hasattr(self.modules[name], "unload"):
                    self.modules[name].unload()
                rm_list = []
                for command in self.commands:
                    if self.commands[command].__module__ == name:
                        rm_list.append(command)
                for command in rm_list:
                    del self.commands[command]

                for event in self.events:
                    rm_list.clear()
                    for handler in self.events[event]:
                        if handler.__module__ == name:
                            rm_list.append(handler)
                    for handler in rm_list:
                        self.events[event].remove(handler)
                self.modules[name] = reload(self.modules[name])

            else:
                self.modules[name] = __import__(name)

            if hasattr(self.modules[name], "initialize"):
                self.modules[name].initialize(self)
            else:
                ShinobuLog.info("Failed to load module '{}': No 'initialize' method.".format(name), label="ModuleLoader")
        except Exception as e:
            tb = traceback.format_exc()
            print("\n" + tb)
            ShinobuLog.info("({}) Error loading module: {}".format(name.upper(), str(e)), label="ModuleLoader")
            return False
        events_after = len(self.events.values())
        ShinobuLog.info("Loaded module '{}' with [{}] commands, [{}] events.".format(name, self.reg_cmd_num, events_after - events_before), label="ModuleLoader")
        return True

    def unload_module(self, name):
        if hasattr(self.modules[name], "unload"):
            self.modules[name].unload()
        del self.modules[name]
        rm_list = []
        for command in self.commands:
            if self.commands[command].__module__ == name:
                rm_list.append(command)
        for command in rm_list:
            del self.commands[command]

        return True

    async def on_message(self, message:discord.Message):
        if message.author.id == self.user.id:
            return
        try:
            args = shlex.split(message.content)
            command = args[0]
            args = args[1:]
            if command in self.commands:
                handler = self.commands[command]
                if self.can_execute(handler, message.author):
                    if hasattr(handler, "shortopts"):
                        kwargs = {}
                        try:
                            options, arguments = getopt.getopt(args, handler.shortopts, handler.longopts)
                        except Exception as e:
                            await self.send_message(message.channel, e)
                            return
                        for opt, value in options:
                            kwargs[opt.replace("-", "")] = value if value else True

                        await handler(message, *arguments, **kwargs)
                    else:
                        await handler(message, *args)
                else:
                    await self.send_message(message.channel,
                                            "You do not have the proper permissions to execute this command.")
            else:
                for handler in self.events['message']:
                    await handler(message)
        except Exception as e:
            ShinobuLog.info("Exception: " + str(e), label="Message Event")

    async def on_ready(self):
        # self.log_channel = self.get_channel(self.config['log_channel_id'])
        ShinobuLog.info("({}) Connected.".format(self.config['instance_name']), label="Shinobu")
        for module in self.config.get('load', ''):
            self.load_module(module)

        for user in self.get_all_members():
            if user.id in self.config['owners']:
                self.owners.append(user)




class ShinobuLink(discord.Client):
    pass






