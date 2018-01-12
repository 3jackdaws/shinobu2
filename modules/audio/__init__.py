import time
from shinobu import shinobu
from discord import Message
from shinobu.commands import command
from shinobu.events import event
from . import player

from .commands import add_audio, set_volume, advance_audio, get_current_audio






async def on_module_unload():
    print("unloading audio")
    for server in shinobu.servers:
        voice_client = shinobu.voice_client_in(server)
        if voice_client:
            await voice_client.disconnect()




commands = [
    command('--add', add_audio),
    command('--vol', set_volume),
    command('--next', advance_audio),
    command('--get', get_current_audio),
]