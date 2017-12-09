from shinobu.client import *
from shinobu.annotations import *
import discord
from gtts import gTTS



shinobu = None  # type: ShinobuClient


def initialize(instance: ShinobuClient):
    global shinobu
    shinobu = instance
    shinobu.register_event('on_voice_state_update', on_join_channel)
    shinobu.register_command('.follow', follow)


async def follow(message:discord.Message, *args):
    fid = int(args[0])
    try:
        if fid in follow_ids:
            follow_ids.remove(fid)
            for user in shinobu.get_all_members():
                if int(user.id) == fid:
                    break
            await shinobu.send_message(message.channel, 'Stopped following {}'.format(user.name))
        else:
            follow_ids.append(fid)
            for user in shinobu.get_all_members():
                if int(user.id) == fid:
                    break
            await shinobu.send_message(message.channel, 'Following {}'.format(user.name))
    except Exception as e:
        print(str(e))


async def on_join_channel(_, after:discord.Member):
    global follow_ids

    if int(after.id) in follow_ids:
        if after.voice.voice_channel:
            if shinobu.is_voice_connected(after.server):
                vc = shinobu.voice_client_in(after.server)
                await vc.disconnect()
            voice_client = await shinobu.join_voice_channel(after.voice.voice_channel)  # type: discord.VoiceClient
            player = voice_client.create_ffmpeg_player('bitch.mp3', use_avconv=True)
            player.start()
            player.join()
        else:
            print("No voice channel")
    else:
        print(after.id, follow_id)
    print('AFTER VC', after.voice.voice_channel)


async def info(before, after:discord.Member):
    vc = after.voice.voice_channel
    print(vc)
    print(type(vc))
