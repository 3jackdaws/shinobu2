from discord import Member
from shinobu import shinobu

LOG_CHANNEL = '264885180345352192'
async def on_member_join(member:Member):
    channel = await shinobu.get_channel(LOG_CHANNEL)
    await shinobu.send_message(channel, f'{member.name} has joined the server')

async def on_member_remove(member:Member):
    channel = await shinobu.get_channel(LOG_CHANNEL)
    await shinobu.send_message(channel, f'{member.name} has left the server')