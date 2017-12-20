

class DiscordIPIUtilities:
    def __init__(self, message):
        self.user = message.author
        self.channel = message.channel
        self.server = message.channel.server



class UserEvents:
    listeners = {
        'message':[]
    }
    @classmethod
    def on(cls, event, handler):
        if event not in UserEvents.listeners:
            raise Exception('That event isn\'t supported')

        cls.listeners[event].append(handler)

    
