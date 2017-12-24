from peewee import *
from shinobu import shinobu
from shinobu.utilities import Logger
from datetime import datetime

BEGINNING_BALANCE = 10000  # millifavors

class FavorUser(Model):
    user_id = BigIntegerField()
    millifavors = BigIntegerField()

    class Meta:
        database = shinobu.db


class FavorTransaction(Model):
    credit_user = ForeignKeyField(FavorUser, related_name='transaction_creditor')
    debit_user = ForeignKeyField(FavorUser, related_name='transaction_debitor')
    millifavors = BigIntegerField()
    reason = CharField(max_length=1000)
    datetime = DateTimeField(default=datetime.now)

    def nicedate(self):
        return self.datetime.strftime("%b %d, %I:%M%p")

    def amount_formatted(self):
        return '{:0.3f}'.format(self.millifavors/1000.0)

    class Meta:
        database = shinobu.db


for model in [FavorUser, FavorTransaction]:
    if not model.table_exists():
        with Logger.reporter():
            model.create_table()


def get_user_or_create_new(userid) -> FavorUser:
    try:
        user = FavorUser.get(FavorUser.user_id == userid)
    except:
        user = FavorUser.create(user_id=userid, millifavors=BEGINNING_BALANCE)
        user.save()
    return user

def favor_transaction(credit_id, debit_id, millifavors, reason=''):
    credit_user = get_user_or_create_new(credit_id)
    debit_user = get_user_or_create_new(debit_id)

    if debit_user.millifavors < millifavors:
        raise Exception('Insufficient favor balance.')

    debit_user.millifavors -= millifavors
    credit_user.millifavors += millifavors


    transaction = FavorTransaction.create(
        credit_user=credit_user,
        debit_user=debit_user,
        millifavors=millifavors,
        reason=reason
    )

    transaction.save()
    credit_user.save()
    debit_user.save()

    return True

def get_balance(user_id):
    print(user_id)
    user = get_user_or_create_new(user_id)
    balance = user.millifavors
    return balance/1000.0