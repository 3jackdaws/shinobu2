import inspect




def permissions(*roles):
    def set_property(command_function):
        command_function.permissions = roles
        return command_function
    return set_property

def help(str):
    def set_property(command_function):
        command_function.help = str
        return command_function
    return set_property

def ignore_paused(command_function):
    command_function.privileged = True
    return command_function

class ShinobuCommand:
    __slots__ = ['name', 'handler', 'group']
    def __init__(self, name, handler, *, group=None):
        self.name = name
        self.handler = handler
        self.group = group

    async def __call__(self, message, *args, **kwargs):
        from shinobu import shinobu, Logger
        with Logger.reporter():
            if inspect.isasyncgenfunction(self.handler):
                async for response in self.handler(message, *args, **kwargs):
                    await shinobu.send_message(message.channel, response)
            else:
                response = await self.handler(message, *args, **kwargs)
                if response:
                    await shinobu.send_message(message.channel, response)

    @property
    def help(self):
        print(self.handler.__doc__)
        return None


command = ShinobuCommand




