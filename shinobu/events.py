
from shinobu import shinobu
from shinobu.utilities import parse_args, Logger
from discord import Message
import inspect
from inspect import Parameter
from getopt import getopt

@shinobu.event
async def on_message(message: Message):
    if message.author == shinobu.user:
        return
    args = parse_args(message.content)
    command = args[0]
    args = args[1:]
    handler = shinobu.commands.get(command)
    if handler:
        signature = inspect.signature(handler)
        parameters = signature.parameters
        if 'args' in parameters and parameters['args'].kind is Parameter.VAR_POSITIONAL:
            pass
        else:
            args = ()

        try:
            await handler(message, *args)
        except Exception as e:
            Logger.error()


@shinobu.event
async def on_ready():
    Logger.info(f'Connected as {shinobu.user}')