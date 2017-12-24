import time

from shinobu.command import *
from shinobu.utilities import alias
# try:
#     player = reload(player)
# except:
#     from . import player
from . import player
from .sc import *

shinobu = None  # type: ShinobuClient


def initialize(instance: ShinobuClient):
    global shinobu
    shinobu = instance
    shinobu.register_command(".soundcloud", soundcloud)
    shinobu.register_command(".sc", soundcloud)
    shinobu.register_command(".music", music)
    shinobu.register_command(".getcurrent", getcurrent)
    shinobu.register_command("--next", alias(music, next=True))
    shinobu.register_command("--pause", alias(music, pause=True))
    shinobu.register_command("--add", add)
    shinobu.register_command("--vol", vol)





def unload():
    print("unloading audio")
    for server in shinobu.servers:
        voice_client = shinobu.voice_client_in(server)
        if voice_client:
            shinobu.invoke(voice_client.disconnect())



@arguments("t", ["help"])
@helpmsg("""`
soundcloud - Soundcloud Downloader
Usage: soundcloud <song url>
`""")
@permissions("everyone")
async def soundcloud(message: Message, *args, t=None, help=False):
    if help:
        await shinobu.send_message(message.channel, soundcloud.helpmsg)
        return
    start_time = time.time()
    url = None
    downloading_str = "Downloading __{}__ [{}]"
    if t:
        url = t
    else:
        if len(args) > 0:
            url = args[0]
        else:
            await shinobu.send_message(message.channel, "You must provide a url to download.")
            return
    track_obj = resolve(url)
    title = track_obj['title']
    author = track_obj['user']['username']
    await shinobu.send_message(message.channel, "__{}__ - *{}*".format(author, title))
    status_message = await shinobu.send_message(message.channel, "Downloading File")
    filename = author + " - " + title + ".mp3"
    stream = get_stream_as_resource(track_obj)

    with open("/tmp/" + filename, "wb+") as file:
        file.write(stream.read())
        file.close()

    await shinobu.edit_message(status_message, "Writing Metadata")
    audio = mutagen.File("/tmp/" + filename)
    audio.add_tags()
    audio = sc.set_artist_title(audio, track_obj['user']['username'], track_obj['title'])

    audio = sc.embed_artwork(audio, sc.get_300px_album_art(track_obj))
    audio.save("/tmp/" + filename, v1=2)
    with open("/tmp/" + filename, "rb") as file:
        await shinobu.edit_message(status_message, "Uploading File")
        await shinobu.send_typing(message.channel)
        await shinobu.send_file(message.channel, file)
        await shinobu.delete_message(status_message)
        file.close()
    duration = time.time() - start_time
    await shinobu.send_message(message.channel, "Total process time: {} seconds".format(round(duration, 2)))


async def request_audio_session(message:Message):
    author_channel = message.author.voice.voice_channel
    if not author_channel:
        await shinobu.send_message(message.channel, "You must be in a voice channel to use this command.")
        return False
    voice_client = shinobu.voice_client_in(message.server)
    if not voice_client:
        return await shinobu.join_voice_channel(author_channel)
    elif voice_client.channel != author_channel:
        await shinobu.send_message(message.channel, "You must be in the same channel as Shinobu to use this command.")
        return False
    else:
        return voice_client

@permissions("everyone")
async def getcurrent(message:Message):
    global controller
    filename = controller.get_current().file
    with open(filename, "rb") as file:
        await shinobu.send_typing(message.channel)
        try:
            await shinobu.send_file(message.channel, file)
        except Exception as e:
            await shinobu.send_message(message.channel, str(e))
        file.close()
try:
    controller
except:
    controller = None

@permissions("everyone")
@helpmsg("""```
music - Play music in a channel
Usage: music [--add <url>] [--next] [--stop] [--pause]
Options:
   --add <url>     (Adds the audio at <url> to the audio queue.)
   --list          (Lists the audio in the current audio queue.)
   --next          (Stops the current song and starts playing the next.)
   --current       (Displays the currently playing song.)
   --stop          (Stops audio playback and causes shinobu to leave the channel.)
   --pause         (Pauses audio playback.)
   --volume <50>   (Sets the output volume to 50%.)
   -p              (Sets listed page of queued audio. Default is 1)
```""")
@arguments("p:", ["add=", "volume=", "next", "stop", "pause", "help", "resume", "list", "current"])
async def music(message:Message, *args, add=None, next=False, pause=False, help=False,  list=False, volume=None, stop=False, current=False, p=1):
    global controller

    if help:
        await shinobu.send_message(message.channel, music.helpmsg)
        return

    voice_client = await request_audio_session(message)
    if voice_client:
        if not controller:
            controller = player.AudioController(voice_client, shinobu)
    else:
        return

    if add:
        try:
            url = add
            containers = player.get_containers_from(url, message)


            await shinobu.send_message(message.channel, "<@{}> added {} tracks.".format(message.author.id, len(containers)))
            await shinobu.delete_message(message)
            for container in containers:
                controller.append(container)
        except player.AudioException as e:
            print(e)
            await shinobu.send_message(message.channel, str(e))
        except Exception as e:
            import traceback
            traceback.print_exc()
            shinobu.log(str(e), label='AudioPlayer')

    if next:
        controller.next()

    if pause:
        controller.toggle_pause()

    if list:
        output = "Audio Queue (Page {}):\n".format(p)
        lower = p*10 - 10
        upper = p*10
        if lower == 0:
            container = controller.get_current()
            output += "__Playing Now:__\n**{}** - *{}*\n( <{}> )\n".format(container.artist, container.title, container.url)
        try:
            for i,container in enumerate(controller.queue[lower:], start=1):
                output += "{}.  **{}** - *{}*  ( <{}> )\n".format(i+lower,container.artist, container.title, container.url)
                if i == upper:break
        except Exception as e:
            pass
        print(lower, upper)
        await shinobu.send_message(message.channel, output)
        return

    if current:
        container = controller.get_current()
        output = "**{}** - __{}__\nUse '.getcurrent' to download and post to channel.".format(container.artist, container.title)
        await shinobu.send_message(message.channel, output)

    if volume:
        if volume is True:
            volume = 100
        else:
            volume = int(volume)
        controller.set_volume(volume)

    if stop:
        await controller.stop()
        controller = None

@permissions("everyone")
async def add(message:Message, *args):
    track=args[0]
    await music(message, add=track)

@permissions("everyone")
async def vol(message:Message, *args):
    vol=int(args[0])
    await music(message, volume=vol)


