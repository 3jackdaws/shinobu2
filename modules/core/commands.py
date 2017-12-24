from shinobu import shinobu, Shinobu
from shinobu.utilities import parse_args
from shinobu import command
from discord import Message

@shinobu.command('.load')
@command.help('''
    {invocation} <module_name>
''')
async def load_module(message:Message, *args):
    if not args:
        return

    module_name = args[0]
    response = ''
    try:
        if shinobu.load_module(module_name):
            response = f'Loaded module "{module_name}"'
        else:
            response = f'Module "{module_name}" already loaded.  Try the ".reload" or ".unload" commands.'
    except ImportError as e:
        response = f'Could not find module "{module_name}"'

    await shinobu.send_message(message.channel, response)


@shinobu.command('.unload')
@command.help('''
    {invocation} <module_name>
''')
async def unload_module(message:Message, *args):
    if not args:
        return

    module_name = args[0]
    response = ''
    try:
        if shinobu.unload_module(module_name):
            response = f'Loaded module "{module_name}"'
        else:
            response = f'Module "{module_name}" already loaded.  Try the ".reload" or ".unload" commands.'
    except ImportError as e:
        response = f'Could not find module "{module_name}"'

    return response


@shinobu.command('.help')
@command.help('''
{invocation} [ module | command ]
''')
async def shinobu_help(message:Message, *args):
    response = ''
    if args:
        object_name = args[0]
        if object_name in shinobu.commands:
            handler = shinobu.commands[object_name]
            if hasattr(handler, 'help'):
                response = handler.help.format(invocation=handler.invocation)
            else:
                response = f'No help available for command "{object_name}"'

        elif object_name in shinobu.modules:
            active_module = shinobu.modules[object_name]
            if hasattr(active_module, 'description'):
                response = active_module.description
            else:
                response =  f'No help available for module "{object_name}"'

        else:
            response = f'Could not find a reference to object "{object_name}"'


    else:
        response = shinobu_help.help.format(invocation=shinobu_help.invocation)
    return response



@shinobu.command('.instance')
@command.ignore_paused
@command.help('''
{invocation} <active|pause|unpause|status>
''')
async def display_instance(message:Message, *args):
    if args:
        subcommand = args[0]
        if subcommand == 'active':
            if not shinobu.modules['core'].events.PAUSED:
                return f'Instance {shinobu.name}: ACTIVE'
        elif subcommand == 'pause':
            shinobu.modules['core'].events.PAUSED = True
        elif subcommand == 'unpause':
            shinobu.modules['core'].events.PAUSED = False
        elif subcommand == 'status':
            paused = not shinobu.modules['core'].events.PAUSED
            return f'Instance {shinobu.name}: {"ACTIVE" if paused else "DISABLED"}'





@shinobu.command('.reload')
@command.help('''
{invocation} <all|module_name>
''')
async def reload(message:Message, *args):
    pass


@shinobu.command('.about')
async def shinobu_about(message:Message):
    modules = '\n'.join([f'  {m}' for m in shinobu.modules])
    return f'''```
Shinobu Version {shinobu.version}
Database Adaptor: {shinobu.config['database']['type']}
[{shinobu.num_events()}] EVENTS, [{shinobu.num_commands()}] COMMANDS
Modules:
{modules}
```'''





