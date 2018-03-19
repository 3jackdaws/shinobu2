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
    cards = Card.where(name=name).all()
    await shinobu.send_typing(message.channel)

    card_set = []
    card_names = []
    for card in cards:
        if card.multiverse_id and card.name not in card_names:
            card_set.append(card)
            card_names.append(card.name)

    if not card_set:
        return '**No Results**'
    elif len(card_set) > 1:
        return '**Search Returned Multiple Results:**\n' + '\n'.join([card.name for card in card_set])
    else:
        for card in card_set:
            id = getattr(card, "multiverse_id")
            if id:
                img = BytesIO()
                print(card.multiverse_id)
                bytes = await get_image(card.multiverse_id)
                img.write(bytes)
                img.seek(0)
                await shinobu.send_file(message.channel, img, filename=f'{card.name}.jpg')
                return
