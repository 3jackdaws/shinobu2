import os
from subprocess import Popen

import mutagen

from . import sc

DOWNLOAD_DIR = "/tmp/"

def file_from_pafy(pafy):
    artwork_url = pafy.bigthumb
    stream = None
    for stream in pafy.audiostreams:
        print(stream)

        if stream.bitrate == "128k":
            stream = stream
            break
    if not stream:
        stream = pafy.getbestaudio()

    filename = DOWNLOAD_DIR + pafy.title + "." + stream.extension
    filemp3 = DOWNLOAD_DIR + pafy.title + ".mp3"
    if not os.path.exists(filemp3):
        print("DL")
        filename = stream.download(filepath=filename, quiet=True)
        print("CONV")

        p = Popen(["avconv", "-i", filename, filemp3])
        p.wait()

        print("CONV DONE")


        audio = mutagen.File(filemp3)

        audio = sc.set_artist_title(audio, pafy.author, pafy.title)
        audio = sc.embed_artwork(audio, artwork_url)
        audio.save(filemp3, v1=2)
    return filemp3