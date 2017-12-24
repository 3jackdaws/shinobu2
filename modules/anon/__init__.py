from shinobu import shinobu
from shinobu.utilities import Logger
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json
from discord import Message
import random


ANON_CHANNEL = '226152231911555073'
WEBHOOK_URL = 'https://discordapp.com/api/webhooks/253225447230406657/MEEc4eJB0HJnm9HsjejN1WVDRugmWl8wDJvuEoicthDKE05ijAs0Dn55i8C9DCO_yumm'
WEBHOOK_ID = None
USER_MAPPING = ''
HEADERS = {
    'User-Agent':'ShinobuWebhookExecutor v1.0',
    'Content-Type': 'application/json'
}

def webhook_send_message(content, *, username=None, avatar_url=None):
    data = {'content':content}
    if username:
        data['username'] = username

    if avatar_url:
        data['avatar_url'] = avatar_url
    request = Request(WEBHOOK_URL, data=json.dumps(data).encode(), headers=HEADERS)
    urlopen(request).read()

@shinobu.event
async def on_ready():
    #Check for webhook
    global WEBHOOK_ID
    request = Request(WEBHOOK_URL, headers=HEADERS)
    try:
        webhook = json.loads(urlopen(request).read().decode())
        WEBHOOK_ID = webhook['id']
        if webhook['name'] != 'anonymous':
            raise
    except Exception as e:
        Logger.error(str(e))
        Logger.warn('Problem with webhook in anonymous channel')

# @shinobu.event
# async def on_message(message: Message):



ANON_EMOJIS = [
    '👌',
    '💡',
    '🤔',
    '😂',
    '🔥',
    '😩',
    '💪'
]

@shinobu.command('.anon')
async def anonymous_post(message:Message):
    if not message.channel.is_private:
        return 'This command must be used in a private channel.'
    status_message = await shinobu.send_message(message.channel, 'Anon posting mode is ON.  Type `.exit` to turn off.')
    emoji = ANON_EMOJIS.pop(0)


    message = await shinobu.wait_for_message(author=message.author, channel=message.channel)

    while message.content != '.exit':

        webhook_send_message(message.content, username=f'{emoji} anonymous {emoji}')
        message = await shinobu.wait_for_message(author=message.author, channel=message.channel)

    await shinobu.send_message(message.channel, 'Anon posting mode is OFF.')
    ANON_EMOJIS.append(emoji)