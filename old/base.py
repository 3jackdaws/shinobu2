from shinobu.client import *
from shinobu.commands import *
from shinobu.utilities import ShinobuConfig
import asyncio
import re
import os

shinobu = None #type: ShinobuClient

def initialize(instance:ShinobuClient):
    global shinobu
    shinobu = instance
    if not shinobu.register_event("on_message", message_log):
        print("Failed registering event")
    shinobu.register_command(".reload", reload)
    shinobu.register_command(".reload_cfg", reload_config)
    shinobu.register_command(".module", module)
    shinobu.register_command(".log", log)
    shinobu.register_command(".help", help)
    shinobu.register_command(".who", who)
    shinobu.register_command("!reboot", shutdown)
    shinobu.register_command(".inspect", inspect)
    shinobu.register_command("#", py_exec)


last_channel = None
async def message_log(message:Message):
    if message.author.id == shinobu.user.id:
        return
    if message.channel != shinobu.log_channel:
        global last_channel
        if message.channel != last_channel:
            last_channel = message.channel
            shinobu.log("[ Channel:    {}   ]".format(message.channel.name))
        shinobu.log("[{}]: {}".format(message.author.name, message.content))


@arguments()
async def reload(message:Message, *args):
    if len(args) > 0:
        module_name = args[0]
    else:
        for module in shinobu.modules:
            shinobu.load_module(module)

@arguments()
async def reload_config(message):
    ShinobuConfig.reload()

@arguments("ulr", ["load", "unload", "reload", "soft"])
async def module(message:Message, *args, u=False, l=False, load=False, unload=False, r=False, reload=False, soft=False):
    print(u)
    response_text = ""
    if len(args) > 0:
        module_name = args[0]
        if u or unload:
            if shinobu.unload_module(module_name):
                response_text = "Module '{}' unloaded successfully.".format(module_name)
            else:
                response_text = "Could not unload module '{}'.".format(module_name)
        elif l or load:
            if module_name not in shinobu.modules:
                if shinobu.load_module(module_name):
                    response_text = "Module '{}' loaded successfully".format(module_name)
            else:
                response_text = "Module '{}' is already loaded".format(module_name)

        elif r or reload:
            if shinobu.load_module(module_name, soft_reload=soft):
                response_text = "Reloaded '{}'".format(module_name)

    await shinobu.send_message(message.channel, response_text)


@arguments("m")
async def log(message:Message, *args, m=False):
    str = " ".join(args)
    if m:
        str = "\033[36m" + str + "\033[0m"
    shinobu.log(str)


@permissions("everyone")
@arguments()
async def help(message:Message):
    output = "**Shinobu ][ Commands:**\nMany commands will accept the --help argument.\n```"
    for command in shinobu.commands:
        output += command + "\n"
    await shinobu.send_message(message.channel, output + "```")


async def shutdown(message:Message):
    await shinobu.logout()
    exit()


async def who(message:Message):
    instance_name = shinobu.config['instance_name']
    await shinobu.send_message(message.channel, "*Tuturu!* Shinobu desu. ({})".format(instance_name))

@permissions("everyone")
@arguments("", ["command="])
async def inspect(message:Message, *args, command=None, event=None):
    output = ""
    if command:
        if command in shinobu.commands:
            handler = shinobu.commands[command]
            output = "Name: {}\nHas help message: {}\nPermissions: {}".format(
                command,
                True if hasattr(handler, "helpmsg") else False,
                ", ".join(handler.permissions) if hasattr(handler, "permissions") else "Owner"
            )
        else:
            output = "There is no '{}' command registered.".format(command)
    elif event:
        pass

    if output:
        await shinobu.send_message(message.channel, output)


def safe_import(name, globals=None, locals=None, fromlist=[], level=-1):
    if name in [
        "math",
        "re"
    ]:
        return __import__(name)
    else:
        raise ImportError("'{}' not found".format(name))



local_env = {}
user_env = {}
global_env = {
    "__builtins__" : {}
}
@arguments("", [])
@permissions("Lancaster House")
async def py_exec(message:Message, *args):
    global local_env, user_env, global_env
    if message.author.id not in user_env:
        user_env[message.author.id] = {}
    config = shinobu.config

    text = message.content
    code = text[2:]

    if '```' in text:
        code = text.split('```')[1]

        code = "\n".join(code.split("\n")[1:])

    def print_to_channel(*args):
        print("Printing")
        shinobu.invoke(shinobu.send_message(message.channel, " ".join([str(x) for x in args])))

    def locals():
        return dict(local_env).items()

    def safe_open(filename, mode="r"):
        user_path = "userfiles/" + message.author.id
        filename = re.sub("[^a-z]", "", filename)
        print(filename)
        if not os.path.exists(user_path):
            os.mkdir(user_path)
        return open(user_path + "/" + filename, mode)

    local_env.update(**user_env[message.author.id])
    local_env["me"] = message.author
    global_env['print'] = print_to_channel
    global_env['__import__'] = safe_import
    global_env['__builtins__']['__import__'] = safe_import
    global_env['__builtins__']['open'] = safe_open
    try:
        exec(code, global_env, local_env)
    except Exception as e:
        print(e)
        print_to_channel("```" + str(e) + "```")

    # user_env.save()




