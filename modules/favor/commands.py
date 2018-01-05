from shinobu import shinobu
from discord import Message, utils
from shinobu import commands
from shinobu.utilities import author_response
from .models import FavorTransaction, FavorUser, favor_transaction, get_balance, get_user_or_create_new




async def credit_user(message:Message, *args):
    try:
        user = message.mentions[0] if message.mentions else None
        amount = float(args[1])

        millicredits = int(amount * 1000)
        reason = args[2]
    except:
        yield credit_user.help.format(invocation=credit_user.invocation)
        return



    yield f'Transfer {amount} favor credits to {user.name}? (yes/no)'
    msg = await author_response()
    confirmation = msg.content
    while confirmation not in ['yes', 'no']:
        yield 'Enter "yes" or "no"'
        msg = await author_response()
        confirmation = msg.content

    if confirmation == 'yes':
        try:
            favor_transaction(user.id, message.author.id, millicredits, reason)
            yield 'Transaction Completed'
        except Exception as e:
            yield str(e)

    return



@shinobu.command('.bal')
async def userbalance(message:Message, *args):
    yield str(get_balance(message.author.id)) + ' FavorCredit'


UserCache = {}
async def user_fetch(user_id):
    global UserCache
    user = UserCache.get(user_id) or await shinobu.get_user_info(user_id)
    UserCache[user_id] = user
    return user

@shinobu.command('.transactions')
async def list_transactions(message:Message):
    user = get_user_or_create_new(message.author.id)
    transactions = FavorTransaction.select().where((FavorTransaction.credit_user == user) | (FavorTransaction.debit_user == user))
    transactions = sorted(transactions, key=lambda x: x.datetime, reverse=True)
    await shinobu.send_typing(message.channel)
    response = f'***Transactions involving __{message.author.name}__:***\n'
    for transaction in transactions:
        debit_user = await user_fetch(transaction.debit_user.user_id)
        credit_user = await user_fetch(transaction.credit_user.user_id)

        if debit_user == message.author:
            response += f'**-** [`{transaction.amount_formatted()}`] to __{credit_user.name}__ ({transaction.nicedate()})\n'
        else:
            response += f'**+** [`{transaction.amount_formatted()}`] from __{debit_user.name}__ ({transaction.nicedate()})\n'



    yield response
    return