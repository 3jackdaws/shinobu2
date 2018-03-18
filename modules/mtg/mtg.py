from discord import Message
import aiohttp
from mtgsdk import Card
from shinobu import shinobu
from io import BytesIO


async def get_resource(url) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session as conn:
            async with conn.request('GET', url) as request:
                return await request.content.read()


async def get_image(multiverse_id):
    url = f'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={multiverse_id}&type=card'
    return await get_resource(url)


async def card_img_from_name(message:Message, *args):
    name = " ".join(args)
    print(name)
    card = Card.where(name=name).all()[0]
    print(card.name)
    img = BytesIO()
    bytes = await get_image(card.multiverse_id)
    img.write(bytes)
    img.seek(0)
    await shinobu.send_file(message.channel, img, filename=f'{card.name}.jpg')
