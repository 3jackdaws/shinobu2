
try:
    from importlib import reload
    for mod in [modules, builtin, misc]:
        reload(mod)
except:
    from . import modules, builtin, misc
from shinobu.commands import command
from shinobu.events import event



commands = [
    command('.load', modules.load_module, group='Module Commands'),
    command('.unload', modules.unload_module, group='Module Commands'),
    command('.reload', modules.reload_module, group='Module Commands'),

    command('.reset', misc.reset_shinobu, group='Info Commands'),
]

events = [
    event("on_message", builtin.on_message),
    event("on_ready", builtin.on_ready),
    event("on_error", builtin.on_error),
]



