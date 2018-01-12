from shinobu.events import event
from .events import on_member_join, on_member_remove

events = [
    event('on_member_remove', on_member_remove),
    event('on_member_join', on_member_join),
]