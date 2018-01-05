
class ShinobuEvent:
    __slots__ = ['type', 'handler', 'group']
    def __init__(self, type, handler, *, group=None):
        self.type = type
        self.handler = handler
        self.group = group

    async def __call__(self, *args, **kwargs):
        from shinobu import Logger
        with Logger.reporter():
            await self.handler(*args, **kwargs)

    def __hash__(self):
        return hash((self.handler.__module__, self.handler.__name__,))

    def __eq__(self, other):
        return type(other) is ShinobuEvent and other.name == self.name and other.module == self.module

    def __repr__(self):
        return f'{self.module}.{self.name}'

    @property
    def name(self):
        return self.handler.__name__

    @property
    def module(self):
        return self.handler.__module__


    @property
    def help(self):
        print(self.handler.__doc__)
        return None


event = ShinobuEvent