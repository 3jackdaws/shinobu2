from discord import Message, VoiceClient
from shinobu import shinobu, Logger
from . import player
import asyncio
from shinobu.utilities import rtfembed


async def request_audio_session(server, channel, author) -> (VoiceClient, player.AudioController):
    global audio_controllers
    author_channel = author.voice.voice_channel
    if not author_channel:
        await shinobu.send_message(channel, "You must be in a voice channel to use this command.")
        return False
    voice_client = shinobu.voice_client_in(server)
    if not voice_client:
        voice_client = await shinobu.join_voice_channel(author_channel)
    elif voice_client.channel != author_channel:
        await shinobu.send_message(channel, "You must be in the same channel as Shinobu to use this command.")
        return False

    if not server in audio_controllers:
        audio_controllers[server] = player.AudioController(voice_client)

    return voice_client, audio_controllers[server]


try:
    audio_controllers
except:
    audio_controllers = {}



async def add_audio(message:Message, *args):
    author = message.author
    channel = message.channel
    server = message.server

    await shinobu.delete_message(message)
    status_message = await shinobu.send_message(channel, f"<@{author.id}> added <{args[0]}>")
    voice_client, controller = await request_audio_session(server, channel, author)


    with Logger.reporter(limit=10):
        url = args[0]
        containers = player.get_containers_from(url, channel, author)

        for container in containers:
            controller.append(container)
        status_message = await shinobu.edit_message(status_message, f'<@{author.id}> added {len(containers)} tracks')
        await asyncio.sleep(5)
        await shinobu.delete_message(status_message)



async def set_volume(message:Message, *args):
    try:
        volume = int(args[0])
        if volume < 200 and volume > 0:
            audio_controllers[message.server].set_volume(volume)
    except:
        pass
    await shinobu.delete_message(message)


async def advance_audio(message:Message):
    audio_controllers[message.server].next()
    await shinobu.delete_message(message)


async def list_audio(message, *args):
    pass




async def get_current_audio(message:Message, *args):
    container = audio_controllers[message.server].get_current()
    if container:
        filename =  container.file
        await shinobu.send_typing(message.channel)
        await shinobu.send_file(message.channel, open(filename, 'rb'), filename=f'{container.artist} - {container.title}')
