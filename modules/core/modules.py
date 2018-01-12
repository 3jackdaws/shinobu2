from shinobu import shinobu, Logger
from shinobu.utilities import rtfembed, StopPropagation
from discord import Message


async def load_module(message:Message, *args):
    '''
    {command} <module_name>
    '''
    if not args:
        return "Load which module?"

    module_name = args[0]
    response = ''
    with Logger.reporter():
        shinobu.load_module(module_name)
        return f'Loaded module "{module_name}"'





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




async def reload_module(message:Message, *args):
    if args:
        module_name = args[0]

        if module_name in shinobu.modules:
            try:
                shinobu.load_module(module_name)
                yield f'Reloaded module "{module_name}"'
            except:
                yield f'Failed reloading module "{module_name}"'
    else:
        for event_name in shinobu.events:
            shinobu.events[event_name].clear()
        for module_name in shinobu.modules.copy():
            shinobu.load_module(module_name)
        yield 'Reloaded'
        raise StopPropagation()




