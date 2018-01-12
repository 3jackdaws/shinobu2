from shinobu import shinobu
from shinobu.utilities import rtfembed
from discord import Message


async def vshow_info(message:Message, *args):
    attribute = args[0]

    if attribute == 'modules':
        FIELD_FORMAT = '{: <10} {: >3} {: >3}'
        result = [f'```markdown']
        result.append(FIELD_FORMAT.format('#MOD', 'CMD', 'EVT'))
        for name, module in shinobu.modules.items():
            result.append(
                FIELD_FORMAT.format(
                    name.lower(),
                    len(getattr(module, 'commands', [])),
                    len(getattr(module, 'events', [])),
                )
            )
        result.append('```')
        return '\n'.join(result)
    elif attribute == 'events':
        FIELD_FORMAT = '{: <16} {: >16} {: >16}'
        result = [f'```markdown']
        result.append(FIELD_FORMAT.format('#MODULE', 'EVENT', 'HANDLER'))
        for event_name, handler_list in shinobu.events.items():
            for handler in handler_list:
                result.append(FIELD_FORMAT.format(handler.module, event_name, handler.name))
        result.append('```')
        return '\n'.join(result)
    elif attribute == 'commands':
        pass




async def reset_shinobu(message:Message):
    yield "Resetting"
    await shinobu.close()