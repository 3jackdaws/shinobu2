from shinobu.client import ShinobuClient, Message
from shinobu.annotations import *
from subprocess import Popen, PIPE
from .utilities import DiscordIPIUtilities
import re



shinobu = None #type: ShinobuClient
def initialize(instance:ShinobuClient):
    global shinobu
    shinobu = instance
    shinobu.register_command(".ipi", ipi)


try:
    local_environment
    global_environment
except NameError:
    local_environment = {}
    global_environment = {}

@arguments()
async def ipi(message:Message, *args):
    author = message.author
    await shinobu.send_message(message.channel, "```md\n# Interactive Python Interpreter\n[{} Local Symbols]\n```".format(len(local_environment)))

    locals = local_environment.copy()
    globals = global_environment.copy()
    globals['print'] = lambda *a: shinobu.invoke(shinobu.send_message(message.channel, ' '.join([str(x) for x in a])))
    globals['discord'] = DiscordIPIUtilities(message)
    while 1:
        message = await shinobu.wait_for_message(author=author, channel=message.channel)
        code = message.content.strip()
        if '```' in code:
            code = re.sub('[`]{3}', '', code)
            exec_func = exec
        else:
            exec_func = eval
        try:
            print(code)
            output = exec_func(code, globals, locals)
        except SystemExit as s:
            break
        except Exception as e:
            output = str(e) or '!!!'
        if output:
            await shinobu.send_message(message.channel, str(output)[:1000])

    local_environment.update(**locals)
    global_environment.update(**globals)
    await shinobu.send_message(message.channel, 'IPI Mode OFF')