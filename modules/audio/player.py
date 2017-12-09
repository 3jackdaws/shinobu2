import discord
from shinobu.client import ShinobuClient, Channel, Message, Member
from . import sc, yt
import mutagen
import pafy
from subprocess import Popen
import os
import shlex
DOWNLOAD_DIR = "/tmp/shinobu/"
sc.DOWNLOAD_DIR = DOWNLOAD_DIR
yt.DOWNLOAD_DIR = DOWNLOAD_DIR
if not os.path.exists(DOWNLOAD_DIR):
    os.mkdir(DOWNLOAD_DIR)


class AudioException(Exception):
    pass


class AudioContainer:
    title       = ""
    artist      = ""
    duration    = -1
    url         = None
    file        = None
    client      = None #type: ShinobuClient
    is_ready = False

    def __init__(self, url, message:Message, shinobu:ShinobuClient):
        self.url = url
        self.file = None
        self.adder = message.author
        self.text_channel = message.channel
        self.client = shinobu

    def resolve(self):

        if "soundcloud" in self.url:
            track = sc.resolve(self.url)
            self.title = track['title']
            self.artist = track['user']['username']
            self.duration = int(track['duration'] / 1000)
            self.track = track
            if not self.track['streamable']:
                raise AudioException("Track '%s' not streamable :(" % self.title)
        elif "youtube" in self.url:
            print("P:", self.url)
            video = pafy.new(self.url)
            self.title = video.title
            self.artist = video.author
            self.stream = None
            self.artwork_url = video.bigthumb
            for stream in video.audiostreams:
                print(stream)

                if stream.bitrate == "128k":
                    self.stream = stream
                    break
            if not self.stream:
                self.stream = video.getbestaudio()
        else:
            raise AudioException("URL not supported: {}".format(self.url))


    def prepare(self):
        if self.is_ready:
            return
        if "soundcloud" in self.url:
            self.file = sc.file_from_track(self.track)
            self.is_ready = True
        elif "youtube" in self.url:
            filename = DOWNLOAD_DIR + self.title + "." + self.stream.extension
            filemp3 = DOWNLOAD_DIR + self.title + ".mp3"
            if not os.path.exists(filemp3):
                print("DL")
                filename = self.stream.download(filepath=filename, quiet=True, remux_audio=True)
                print("CONV")

                p = Popen(["avconv", "-i", filename, filemp3])
                p.wait()

                print("CONV DONE")
                self.file = filemp3

                audio = mutagen.File(self.file)

                audio = sc.set_artist_title(audio, self.artist, self.title)
                audio = sc.embed_artwork(audio, self.artwork_url)
                audio.save(self.file, v1=2)
            self.is_ready = True

        else:
            raise AudioException("URL not supported: {}".format(self.url))


class YouTubeAudioContainer:
    def __init__(self, pafy_object, message):
        self.duration = pafy_object.length
        self.added_by = message.author
        self.channel = message.channel
        self.pafy = pafy_object
        self.file = None
        self.is_ready = False

    @property
    def title(self):
        return self.pafy.title

    @property
    def artist(self):
        return self.pafy.author

    @property
    def url(self):
        return "http://youtube.com/watch?v=" + self.pafy.videoid

    def prepare(self):
        self.file = yt.file_from_pafy(self.pafy)
        self.is_ready = True


class SoundCloudAudioContainer():
    def __init__(self, track:dict, message:Message):
        self.duration = int(track['duration']/1000)
        self.added_by = message.author
        self.channel = message.channel
        self.track = track
        self.file = None
        self.is_ready = False

    def __str__(self):
        return "SoundCloudAudioContainer<[{}] {} - {}>".format(self.duration, self.artist, self.title)

    @property
    def title(self):
        return self.track['title']

    @property
    def artist(self):
        return self.track['user']['username']

    @property
    def url(self):
        return self.track['permalink_url']

    def prepare(self):
        self.file = sc.track_to_file(self.track)
        print("Prepared track %s " % self.file)
        self.is_ready = True


class AudioController:
    queue = []   # type: [AudioContainer]
    current_sp = None  # type: discord.voice_client.StreamPlayer
    current_container = None
    voice_client = None  # type: discord.VoiceClient
    volume = 0.2

    def __init__(self, voice_client, shinobu):
        self.voice_client = voice_client
        self.shinobu = shinobu

    def next(self):
        if self.current_sp:
            self.current_sp.resume()
            self.current_sp.stop()

    def toggle_pause(self):
        if self.current_sp and not self.current_sp.is_done():
            self.current_sp.pause() if self.current_sp.is_playing() else self.current_sp.resume()

    def set_volume(self, val):
        self.volume = float(val/100)
        self.current_sp.volume = self.volume

    def get_current(self):
        return self.current_container

    def append(self, container:AudioContainer):
        self.queue.append(container)
        self.process()

    def process(self):

        if len(self.queue) > 0:

            if not self.current_sp or self.current_sp.is_done():

                if not self.queue[0].is_ready:
                    self.queue[0].prepare()
                self.current_container = self.queue.pop(0)
                self.current_sp = self.voice_client.create_ffmpeg_player(
                    self.current_container.file,
                    use_avconv=True,
                    after=self.process
                )
                shinobu = self.shinobu
                game = discord.Game(name=self.current_container.artist)
                shinobu.invoke(shinobu.change_presence(game=game))

                shinobu.invoke(
                    shinobu.send_message(self.current_container.channel, "Now playing: **{}** - __{}__".format(
                        self.current_container.artist,
                        self.current_container.title
                    ))  # we're lisp now
                )

                self.current_sp.volume = self.volume
                self.current_sp.start()

                self.process()
            elif not self.queue[0].is_ready:
                print("Preparing: {} - {}".format(self.queue[0].artist, self.queue[0].title))
                self.queue[0].prepare()

    async def stop(self):
        self.queue = []
        await self.voice_client.disconnect()
        self.current_sp.stop()

def get_containers_from(url, message):
    if "soundcloud" in url:
        resource = sc.resolve(url)
        if resource['kind'] == "track":
            return [SoundCloudAudioContainer(resource, message)]
        elif resource['kind'] == "playlist":
            return [SoundCloudAudioContainer(track, message) for track in resource['tracks']]
    elif "youtube" in url:
        if "playlist" in url:
            playlist = pafy.get_playlist(url)
            return [YouTubeAudioContainer(item['pafy'], message) for item in playlist['items']]
        else:
            return [YouTubeAudioContainer(pafy.new(url), message)]
    else:
        return []


