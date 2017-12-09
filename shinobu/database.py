import pymysql
import json
from pymysql.err import OperationalError
__all__ = [
    "initialize",
    "get_connection",
    "MAX_CONNECTIONS"
]

DATABASE = {}
CONNECTIONS = []

connection = None  # type:pymysql.Connection

def initialize(host='localhost', port='3306', db='shinobu', user='shinobu', password=None):
    global connection
    DATABASE.update(host=host, port=port, db=db, user=user, password=password)
    connection = pymysql.Connect(cursorclass=pymysql.cursors.DictCursor, charset='utf8mb4', **DATABASE)
    require_table("ConfigStore", """
        G VARCHAR(128),
        K VARCHAR(128),
        V VARCHAR(60000),
        PRIMARY KEY(G,K)
    """)


def connect():
    global connection
    connection =  pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **DATABASE)


def execute(sql, params=None, show_errors=False, auto_commit=True, cursor=None):
    try:
        if not cursor:
            cursor = connection.cursor()
        cursor.execute(sql, params)
        if auto_commit:
            connection.commit()
        return True, cursor
    except Exception as e:
        if show_errors:
            print(type(e))
            print(e, sql)
        return False, e
    except OperationalError as e:
        connect()


def require_table(table_name, definition):
    success, cursor = execute("SELECT 1 FROM {} LIMIT 1".format(table_name))
    if not success:
        execute("CREATE TABLE {}({})".format(table_name,definition), None, show_errors=True)


class DBDict(dict):
    removed = set()
    updated = set()
    def __init__(self, identifer):
        self.identifier = identifer
        global connection
        success, cursor = execute("SELECT K, V FROM ConfigStore WHERE G=%s", (identifer))  #type: pymysql.cursors.DictCursor
        if success:
            results = cursor.fetchall()
        else:
            results = {}
        super(DBDict, self).__init__(*[{x["K"]: json.loads(x["V"]) for x in results}])

    def save(self):
        sql = """
              INSERT INTO ConfigStore (G, K, V)
              VALUES (%s,%s,%s)
              ON DUPLICATE KEY UPDATE
              V=%s
              """

        for key in self.updated:
            value = json.dumps(self[key])
            execute(sql, (self.identifier, key, value, value), show_errors=True, auto_commit=False)
        for stmt in self.removed:
            execute(stmt, show_errors=True, auto_commit=False)
        connection.commit()

    def __delitem__(self, key):
        super(DBDict, self).__delitem__(key)
        self.removed.add(key)

    def __setitem__(self, key, value):
        super(DBDict, self).__setitem__(key, value)
        if key in self.removed:
            self.removed.remove(key)
        self.updated.add(key)

