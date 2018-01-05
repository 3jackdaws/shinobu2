from shinobu import shinobu
from shinobu.utilities import Logger
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json
from discord import Message, Embed, Reaction



ANON_CHANNEL = ''
WEBHOOK_URL = ''
WEBHOOK_ID = None
USER_MAPPING = ''
HEADERS = {
    'User-Agent':'ShinobuWebhookExecutor v1.0',
    'Content-Type': 'application/json'
}

def webhook_send_message(*, content=None, file_url=None, username=None, avatar_url=None):
    data = {}
    if content:
        data['content'] = content
    if file_url:
        data['content'] = file_url
    if username:
        data['username'] = username

    if avatar_url:
        data['avatar_url'] = avatar_url
    request = Request(WEBHOOK_URL, data=json.dumps(data).encode(), headers=HEADERS)
    urlopen(request).read()

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


    message = await shinobu.wait_for_message(author=author, channel=message.channel)

    while message.content != '.exit':
        if message.content != '.anon':
            file = message.attachments[0] if message.attachments else None
            webhook_send_message(
                content=message.content,
                file_url=file['url'] if file else None,
                username=f'{emoji} anonymous {emoji}'
            )
        message = await shinobu.wait_for_message(author=message.author, channel=message.channel)

    await shinobu.send_message(message.channel, 'Anon posting mode is OFF.')
    del anon_sessions[author]
    ANON_EMOJIS.append(emoji)