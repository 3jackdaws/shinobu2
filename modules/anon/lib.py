from shinobu import shinobu
from shinobu.utilities import Logger
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import requests
import json
from discord import Message, Embed, Reaction
from base64 import b64encode




ANON_CHANNEL = None
WEBHOOK_URL = 'https://discordapp.com/api/webhooks/253225447230406657/MEEc4eJB0HJnm9HsjejN1WVDRugmWl8wDJvuEoicthDKE05ijAs0Dn55i8C9DCO_yumm'
WEBHOOK_ID = None
USER_MAPPING = ''
HEADERS = {
    'User-Agent':'ShinobuBot (http://github.com/3jackdaws/shinobu2, v2.5.0)',
    'Content-Type': 'multipart/form-data',
    'Authorization':f'Bot {shinobu.config["discord"].get("bot_token")}'
}

def webhook_send_message(*, content=None, file_url=None, username=None, avatar_url=None):
    data = {}
    if content:
        data['content'] = content
    if file_url:
        req = Request('http://www.qygjxz.com/data/out/179/5054311-picture.png', headers=HEADERS)
        file = urlopen(req).read()
        data['file'] = b64encode(file)
    if username:
        data['username'] = username

    if avatar_url:
        data['avatar_url'] = avatar_url
    request = Request(WEBHOOK_URL, data=urlencode(data).encode(), headers=HEADERS)
    urlopen(request).read()

async def on_ready():
    #Check for webhook
    global WEBHOOK_ID, ANON_CHANNEL
    request = Request(WEBHOOK_URL, headers=HEADERS)
    try:
        webhook = json.loads(urlopen(request).read().decode())
        WEBHOOK_ID = webhook['id']
        if webhook['name'] != 'anonymous':
            raise
        ANON_CHANNEL = webhook['channel_id']
    except Exception as e:
        Logger.error(str(e))
        Logger.warn('Problem with webhook in anonymous channel')

DISAPPROVAL_EMOJIS = {
    '👎'
}

APPROVAL_EMOJIS = {
    '👍'
}

async def on_reaction_add(reaction:Reaction, user):
    channel = reaction.message.channel
    if channel.id != ANON_CHANNEL:
        return
    if reaction.emoji in APPROVAL_EMOJIS or reaction.emoji in DISAPPROVAL_EMOJIS:

        reaction_emojis = set([x.emoji for x in reaction.message.reactions])
        approvals = APPROVAL_EMOJIS.intersection(reaction_emojis)
        dissaprovals = DISAPPROVAL_EMOJIS.intersection(reaction_emojis)
        if len(dissaprovals) - len(approvals) >= 1:

            await shinobu.delete_message(reaction.message)
            await shinobu.send_message(channel, 'A post was removed for being against the rules of this channel')



ANON_EMOJIS = [
    '👌',
    '💡',
    '🤔',
    '😂',
    '🔥',
    '😩',
    '💪'
]

anon_sessions = {}


async def anonymous_post(message:Message):
    global anon_sessions
    author = message.author
    if not message.channel.is_private:
        await shinobu.delete_message(message)
        await shinobu.send_message(author, 'The `.anon` command can only be used in this DM channel.')
        return



    if author in anon_sessions:
        emoji = anon_sessions[author]
        yield f'Posting as user: {emoji} anonymous {emoji}'
        return

    anon_sessions[author] = emoji = ANON_EMOJIS.pop(0)
    yield f'Posting as user: {emoji} anonymous {emoji}'


    message = await shinobu.wait_for_message(author=author, channel=message.channel)  # type: Message

    while message.content != '.exit':
        if message.content != '.anon':
            for attachment in message.attachments:
                print(json.dumps(attachment, indent=2))
            file = message.attachments[0] if message.attachments else None
            webhook_send_message(
                content=message.content,
                username=f'{emoji} anonymous {emoji}'
            )
        message = await shinobu.wait_for_message(author=message.author, channel=message.channel)

    await shinobu.send_message(message.channel, 'Anon posting mode is OFF.')
    del anon_sessions[author]
    ANON_EMOJIS.append(emoji)