from shinobu import shinobu, Shinobu
from shinobu.utilities import parse_args
from discord import Message

@shinobu.command('.mod')
async def modify_module(message:Message, *args):
    subcommand = args[0] if args else None
    module_name = args[1] if args[1:] else None
    if not (subcommand and module_name):
        await shinobu.send_message(message.channel, f'```\n.mod <load|reload|reset> <module_name>')
        return

    if subcommand in ('load', 'reload',):
        hard_reload = False
    elif subcommand in ('reset',):
        hard_reload = True
    else:
        await shinobu.send_message(message.channel, f'```\n.mod <load|reload|reset> <module_name>')
        return

    if shinobu.load_module(module_name, hard_reload):
        await shinobu.send_message(message.channel, f'Module "{module_name}" sucessfully loaded.')


