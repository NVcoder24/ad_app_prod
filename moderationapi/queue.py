from cfg import *
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2.extras
import time
import http3
import asyncio

# waiting for db
while True:
    try:
        postgre_con = psycopg2.connect(dbname=MOD_POSTGRES_DATABASE, user=MOD_POSTGRES_USERNAME, password=MOD_POSTGRES_PASSWORD, host=MOD_POSTGRES_HOST, port=MOD_POSTGRES_PORT)
        print("DB SETUP FINISHED")
        break
    except Exception as e:
        print("DB SETUP ERROR, RETRY")

while True:
    try:
        # start db connection
        postgre_con = psycopg2.connect(dbname=MOD_POSTGRES_DATABASE, user=MOD_POSTGRES_USERNAME, password=MOD_POSTGRES_PASSWORD, host=MOD_POSTGRES_HOST, port=MOD_POSTGRES_PORT)
        postgre_cur = postgre_con.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # get all swear words
        postgre_cur.execute("SELECT * FROM swear_words")
        swear_words = [ i[0] for i in postgre_cur.fetchall() ]

        # create http client
        client = http3.AsyncClient()

        # get everything in scheduled
        postgre_cur.execute("SELECT * FROM scheduled")
        for task in postgre_cur.fetchall():
            # check for swear words
            is_good = True
            message = ""
            for i in swear_words:
                if i in task["ad_text"].lower().replace(" ", "") or i in task["ad_title"].lower().replace(" ", ""):
                    is_good = False
                    message = "ругательные слова"
                    break
            
            # send results
            try:
                r = asyncio.run(client.post(f"http://{MAINAPI_HOST}/moderation/results", json={
                    "ad_id": task["ad_id"],
                    "is_good": is_good,
                    "message": message
                }))
                if r.status_code != 204: raise Exception("status code not 204!")
                postgre_cur.execute("DELETE FROM scheduled WHERE id=%s", (task["id"],))
            except Exception as e:
                print(f"Failed to send moderation result for ad id {task["ad_id"]} due to: {e}")
        postgre_con.commit()

        # close db connection
        postgre_cur.close()
        postgre_con.close()

        # sleep 1 second to lower load
        time.sleep(1)
    except Exception as e:
        print(f"Queue error: {e}")