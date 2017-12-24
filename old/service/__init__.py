from shinobu.client import ShinobuClient, Message
from shinobu.command import *
from urllib.request import Request, urlopen
import asyncio
from subprocess import Popen, PIPE
from importlib import reload
import re
import hashlib
import os

try:
    service = reload(service)
except:
    from . import service




shinobu = None #type: ShinobuClient
def initialize(instance:ShinobuClient):
    global shinobu
    shinobu = instance
    shinobu.register_command(".nmap", nmap)
    shinobu.register_command(".cat", cat)
    shinobu.register_command(".run", proc)
    shinobu.register_command("$", system)

    # shinobu.register_event("message", r9k)


@permissions("Lancaster House")
@arguments("")
async def trash(message:Message):
    user_dict = {
        "112655461202849792": "Tristan",
        "120732074624679938": "Daniel",
        "142860170261692416": "Ian"
    }

    actor = user_dict[str(message.author.id)]
    task_id = 1



async def nmap(message:Message, *args):
    await shinobu.send_typing(message.channel)
    output = check_output(["nmap", *args]).decode('utf-8')
    await shinobu.send_message(message.channel, output)

@permissions("everyone")
async def cat(message:Message, *args):
    result = service.get_resource("https://thecatapi.com/api/images/get?format=src&type=jpg")
    print(result)
    await shinobu.send_file(message.channel, result, filename="cat.jpg")
    result.close()

async def proc(message:Message, *args):
    await shinobu.send_typing(message.channel)
    try:
        output = check_output(args).decode('utf-8')
    except Exception as e:
        output = str(e)
    await shinobu.send_message(message.channel, "```" + output + "```")

async def system(message:Message, *args):
    await shinobu.send_typing(message.channel)
    command_line = message.content[2:]
    try:
        process = Popen(command_line + ' 2>&1', shell=True, stdout=PIPE)

        output = process.stdout.read().decode() or 'No Output'
    except Exception as e:
        output = str(e)
    await shinobu.send_message(message.channel, "```md\n" + output + "```")



