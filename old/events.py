from shinobu.client import *
from shinobu.command import *
import shlex
import discord
import getopt

shinobu = None  # type: ShinobuClient


def initialize(instance: ShinobuClient):
    global shinobu
    shinobu = instance
    shinobu.register_event('on_message', on_message)
    shinobu.register_event('on_error', on_error)


async def on_message(message: discord.Message):
    if message.author.id == shinobu.user.id:
        return
    try:
        args = shlex.split(message.content)
        command = args[0]
        args = args[1:]
        if command in shinobu.commands:
            handler = shinobu.commands[command]
            if shinobu.can_execute(handler, message.author):
                if hasattr(handler, "shortopts"):
                    kwargs = {}
                    try:
                        options, arguments = getopt.getopt(args, handler.shortopts, handler.longopts)
                    except Exception as e:
                        await shinobu.send_message(message.channel, e)
                        return
                    for opt, value in options:
                        kwargs[opt.replace("-", "")] = value if value else True

                    await handler(message, *arguments, **kwargs)
                else:
                    await handler(message, *args)
            else:
                await shinobu.send_message(message.channel,
                                        "You do not have the proper permissions to execute this command.")
        else:
            for handler in shinobu.events['message']:
                await handler(message)
    except Exception as e:
        shinobu.log("Exception: " + str(e), label="Message Event")


async def on_error(*args, **kwargs):
    print(kwargs)
    shinobu.log("\n".join([str(x) for x in args]), label='ERROR', send_to_channel=True)