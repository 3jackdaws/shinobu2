
from shinobu import shinobu
from shinobu.utilities import parse_args, Logger
from discord import Message
import inspect
from inspect import Parameter


PAUSED = False

@shinobu.event
async def on_message(message: Message):
    if message.author == shinobu.user:
        return
    args = parse_args(message.content)
    command = args[0]
    args = args[1:]
    handler = shinobu.commands.get(command)
    if handler:
        if not hasattr(handler, 'privileged') and PAUSED:
            return
        signature = inspect.signature(handler)
        parameters = signature.parameters
        if 'args' in parameters and parameters['args'].kind is Parameter.VAR_POSITIONAL:
            pass
        else:
            args = ()

        with Logger.reporter():
            if inspect.isasyncgenfunction(handler):
                async for response in handler(message, *args):
                    await shinobu.send_message(message.channel, response)
            else:
                response = await handler(message, *args)
                if response:
                    await shinobu.send_message(message.channel, response)




@shinobu.event
async def on_ready():
    Logger.info(f'Connected as {shinobu.user}')


@shinobu.event
async def on_error(*args):
    print(args)