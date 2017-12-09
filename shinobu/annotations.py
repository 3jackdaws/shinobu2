
def permissions(*roles):
    def set_property(command_function):
        command_function.permissions = roles
        return command_function
    return set_property


def arguments(shortopts="", longopts=[]):
    def set_property(command_function):
        command_function.shortopts = shortopts
        command_function.longopts = longopts
        return command_function
    return set_property

def helpmsg(str):
    def set_property(command_function):
        command_function.helpmsg = str
        return command_function
    return set_property

