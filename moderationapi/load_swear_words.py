import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from cfg import *


postgre_con = psycopg2.connect(dbname=MOD_POSTGRES_DATABASE, user=MOD_POSTGRES_USERNAME, password=MOD_POSTGRES_PASSWORD, host=MOD_POSTGRES_HOST, port=MOD_POSTGRES_PORT)
postgre_cur = postgre_con.cursor()

with open("swear_words.txt", "r", encoding="UTF-8") as f:
    for i in f.readlines():
        postgre_cur.execute("INSERT INTO swear_words (word) VALUES (%s)", (i.strip(),))

postgre_con.commit()

postgre_cur.close()
postgre_con.close()