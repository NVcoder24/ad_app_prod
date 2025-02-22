from fastapi import FastAPI, Request, Response, status
from db import DB
from cfg import *
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import uvicorn

# setup
while True:
    try:
        try:
            postgre_con = psycopg2.connect(dbname="postgres", user=MOD_POSTGRES_USERNAME, password=MOD_POSTGRES_PASSWORD, host=MOD_POSTGRES_HOST, port=MOD_POSTGRES_PORT)
            postgre_con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            postgre_cur = postgre_con.cursor()
            with open("prepare1.sql", "r") as f:
                postgre_cur.execute(f.read().format(MOD_POSTGRES_DATABASE))
                postgre_con.commit()
            postgre_cur.close()
            postgre_con.close()
        except Exception as e:
            pass

        postgre_con = psycopg2.connect(dbname=MOD_POSTGRES_DATABASE, user=MOD_POSTGRES_USERNAME, password=MOD_POSTGRES_PASSWORD, host=MOD_POSTGRES_HOST, port=MOD_POSTGRES_PORT)
        postgre_cur = postgre_con.cursor()
        with open("prepare2.sql", "r") as f:
            postgre_cur.execute(f.read())
            postgre_con.commit()
        postgre_cur.close()
        postgre_con.close()
        
        print("DB SETUP FINISHED")
        break
    except Exception as e:
        print("DB SETUP ERROR, RETRY")

# create app
app = FastAPI()

@app.post("/schedule")
async def schedule(request:Request, response:Response):
    db = DB()

    body = await request.json()

    db.postgre_cur.execute("INSERT INTO scheduled (ad_id, ad_title, ad_text) VALUES (%s, %s, %s)", (body["ad_id"], body["ad_title"], body["ad_text"]))
    db.postgre_con.commit()

    db.end()

@app.get("/swear_words")
async def get_swear_words():
    db = DB()

    db.postgre_cur.execute("SELECT * FROM swear_words")
    resp = [ i[0] for i in db.postgre_cur.fetchall() ]

    db.end()

    return resp

@app.post("/swear_words")
async def post_swear_words(request:Request, response:Response):
    db = DB()

    try:
        for i in await request.json():
            db.postgre_cur.execute("INSERT INTO swear_words (word) VALUES (%s)", (i,))
        db.postgre_con.commit()
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    db.end()

    response.status_code = status.HTTP_201_CREATED

@app.delete("/swear_words")
async def delete_swear_words(request:Request, response:Response):
    db = DB()

    try:
        for i in await request.json():
            db.postgre_cur.execute("DELETE FROM swear_words WHERE word LIKE %s", (i,))
        db.postgre_con.commit()
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    db.end()

    response.status_code = status.HTTP_204_NO_CONTENT

# run the app
if __name__ == "__main__":
    server_address = MODERATION_HOST
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))