from shinobu.client import *
from shinobu.utilities import ShinobuConfig
from shinobu.commands import *
import asyncio
import discord
import re

shinobu = None #type: ShinobuClient

def initialize(instance:ShinobuClient):
    global shinobu, filters
    shinobu = instance
    shinobu.register_command(".pin", pin)
    shinobu.register_command(".ban", ban)
    shinobu.register_command(".say", say)
    shinobu.register_command(".status", status)
    shinobu.register_command(".filter", match)
    shinobu.register_event("on_message", filter_message)


@arguments("", ["help", "remove"])
@helpmsg("""```
pin - pin a message to the current channel
Usage: pin <message id>
Options:
    --remove      (Unpins a message.)
```""")
async def pin(message:Message, *args, remove=False, help=False):
    if help:
        await shinobu.send_message(message.channel, pin.helpmsg)
        return
    message_id = args[0]
    pin_message = await shinobu.get_message(message.channel, message_id)
    if remove:
        await shinobu.unpin_message(pin_message)
    else:
        await shinobu.pin_message(pin_message)


@arguments("", ["help", "idle", "active", "game="])
@helpmsg("""```
status - change the status of Shinobu
Usage: status [-g <Game Name>] [--idle | --active]
Options:
    --idle              (Sets Shinobu to idle.)
    --active            (Sets Shinobu to active.)
    --game <game name>  (Sets Shinobu's currently played game.)
```""")
async def status(message:Message, *args, idle=False, active=False, game=None, help=False):
    if help:
        await shinobu.send_message(message.channel, pin.helpmsg)
        return
    is_idle = None
    if idle:
        is_idle = discord.Status.idle
    elif active:
        is_idle = discord.Status.online
    if game:
        game = discord.Game(name=game)
    await shinobu.change_presence(game=game, status=is_idle)

@arguments("", ["remove=", "add="])
async def create_channel(message:Message, remove=None, add=None):
    pass

filters = ShinobuConfig("filters")
async def filter_message(message:Message):

    channel = message.channel
    for filter_name in filters:
        filter_obj = filters[filter_name]

        if not filter_obj['active']:
            continue

        if filter_obj["channels"] and not message.channel.id in filter_obj['channels']:
            continue

        if filter_obj["users"] and not message.author.id in filter_obj['users']:
            continue

        if re.search(filter_obj['pattern'], message.content):
            action = filter_obj['action']
            if action == "ban":
                await shinobu.ban(message.author, delete_message_days=0)
            elif action == "kick":
                await shinobu.kick(message.author)
            await shinobu.delete_message(message)

            if "message" in filter_obj and len(filter_obj['message']) > 0:
                await shinobu.send_message(channel, filter_obj['message'])



@helpmsg("""```
filter - apply actions to messages based on user, channel, pattern
Usage: .filter --name <filter name> --pattern "regex" --action [ban|remove|kick]
Options:
    --channels    "<channel_id channel_id>"    (Only apply this filter to lsited channels.)
    --users       "<user_id user_id>"          (Only apply this filter to listed users.)
    --msg         "Message to send"            (Send this message to the same channel after matching a pattern.)
    --deactivate                               (Deactivate the named filter.)
```""")
@arguments("", ["list", "users=", "pattern=", "channels=", "action=", "name=", "deactivate", "msg=", "help", "remove"])
async def match(message:Message, users=None, pattern=None, list=False, channels=None, action=None, name=None, deactivate=False, msg=None, help=False, remove=False):
    global filters
    filter_obj = None
    if help:
        await shinobu.send_message(message.channel, match.helpmsg)
        return

    if list:
        out = "Active Filters:\n"
        for filter_name in filters:
            filter_obj = filters[filter_name]
            out += """```
Name:     {}
Active:   {}
Pattern:  "{}"
Users:    {}
Channels: {}
Action:   {}
Message:  {}
            ```""".format(filter_name,
                       filter_obj['active'],
                       filter_obj['pattern'],
                       filter_obj['users'] if filter_obj['users'] else "All",
                       filter_obj['channels'] if filter_obj['channels'] else "All",
                       filter_obj['action'],
                       filter_obj['message'] if "message" in filter_obj else None,
                       )
        await shinobu.send_message(message.channel, out)
        return
    if name in filters:
        filter_obj = filters[name]

    if filter_obj and remove:
        del filters[name]
        return
    if not filter_obj and not (pattern and action and name):
        await shinobu.send_message(message.channel, "Requires --name, --pattern, --action")
        return

    if action and action not in ("remove", "ban", "kick"):
        await shinobu.send_message(message.channel, "Action must be one of: remove, ban, kick")
        return

    if filter_obj:

        filter_obj['active'] = not deactivate

        if pattern:
            filter_obj['pattern'] = pattern

        if users:
            filter_obj['users'] = users.split(" ")

        if channels:
            filter_obj['channels'] = channels.split(" ")

        if action:
            filter_obj['action'] = action

        if msg:
            filter_obj['message'] = msg

        await shinobu.send_message(message.channel, "Altered filter '{}'".format(name))
    else:
        filter_obj = {
            "active":not deactivate,
            "pattern":pattern,
            "users":users.split(" ") if users else None,
            "channels":channels.split(" ") if channels else None,
            "action":action,
            "message":msg,
        }
        await shinobu.send_message(message.channel, "Create Filter '{}'".format(name))

    filters[name] = filter_obj
    filters.save()

@arguments("", ["unban"])
async def ban(message:Message, *args, unban=False):
    user_id = args[0]

    if unban:
        for banned in await shinobu.get_bans(message.server):
            if banned.id == user_id:
                await shinobu.unban(message.server, banned)
    else:
        for user in shinobu.get_all_members():
            if user.id == user_id:
                await shinobu.ban(user, delete_message_days=0)

@arguments("c:")
@helpmsg("""
say - post a message from Shinobu, immediately delete command message
Usage: .say <message>
""")
async def say(message:Message, *args, c=None):
    channel = message.channel
    await shinobu.delete_message(message)
    if c:
        channel_id = re.findall("[0-9]+", c)
        if channel_id:
            channel_id = channel_id[0]
            channel = shinobu.get_channel(channel_id)
    else:
        channel = message.channel

    if channel:
        print(args)
        await shinobu.send_message(channel, " ".join(args))