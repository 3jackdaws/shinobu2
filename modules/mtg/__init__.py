
from shinobu.commands import command
from shinobu.events import event
from . import mtg



commands = [
    command('.mtg', mtg.card_img_from_name, group='Module Commands'),
]




