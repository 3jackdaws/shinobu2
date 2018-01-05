
async def shinobu_help(message:Message, *args):
    __doc__ = '''
    {command} - Display module and command help
    '''
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



@shinobu.command('.pause')
@command.ignore_paused
@command.help('''
{invocation} <active|pause|unpause|status>
''')
async def display_instance(message:Message, *args):
    print(args)


