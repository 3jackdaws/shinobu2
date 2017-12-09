from shinobu.client import ShinobuClient, Message, Channel
import pymysql

shinobu = None #type: ShinobuClient
connection = None #type: pymysql.Connection


def transaction(debit_id, credit_id, amount):
    with connection.cursor() as c:
        c.execute("INSERT INTO ")
