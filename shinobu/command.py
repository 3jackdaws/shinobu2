
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
