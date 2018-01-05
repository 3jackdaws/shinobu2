from shinobu.commands import command
from shinobu.events import event
from .lib import anonymous_post, on_ready, on_reaction_add

commands = [
    command('.anon', anonymous_post)
]

events = [
    event('on_ready', on_ready),
    event('on_reaction_add', on_reaction_add),

]