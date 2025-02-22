import psycopg2
import psycopg2.extras
from cfg import *

class DB:
    def __init__(self):
        self.postgre_con = psycopg2.connect(dbname=MOD_POSTGRES_DATABASE, user=MOD_POSTGRES_USERNAME, password=MOD_POSTGRES_PASSWORD, host=MOD_POSTGRES_HOST, port=MOD_POSTGRES_PORT)
        self.postgre_cur = self.postgre_con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    def end(self):
        self.postgre_cur.close()
        self.postgre_con.close()