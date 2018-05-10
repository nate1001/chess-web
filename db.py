import psycopg2
import sys
import psycopg2.extras
 
class Connection:
    conn_string = "host='localhost' dbname='chess' user='www-data' password='NULL'"
    conn = None

    @classmethod
    def connect(cls):
        cls.conn = psycopg2.connect(cls.conn_string)

    @classmethod
    def cursor(cls):
        return cls.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    @classmethod
    def execute(cls, cursor, query):
        cursor.execute(query)
        return cursor.rowcount, cursor

class Query(Connection):

    @classmethod
    def random_search(cls):
        c = Connection.cursor()
        return cls.execute(c, "select * from random_search()")

Connection.connect()
for row in (Query.random_search())[1]:
    print(row)

    

