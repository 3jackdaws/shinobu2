from shinobu.client import ShinobuClient, Message, Channel
from shinobu.annotations import *
from . import betting, games
import pymysql

config = {}

def initialize(instance:ShinobuClient):
    global shinobu, connection, config
    shinobu = instance
    config = shinobu.config['games_module']
    connection = shinobu.db.get_connection()
    shinobu.register_command("roll", roll)

@options("b:", ["bet="])
async def roll(message:Message, b=None, bet=None):
    odds = config['betting_odds']
    final = games.roll()