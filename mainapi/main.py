from fastapi import FastAPI
from .routers import (ads, 
                      advertisers, 
                      campaigns, 
                      clients, 
                      statistics, 
                      time_,
                      campaigns_img,
                      moderation,
                      tgbot)
from .db import DB
from .cfg import *
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import uvicorn

# SETUP DATABASE
while True:
    try:
        try:
            postgre_con = psycopg2.connect(dbname="postgres", user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
            postgre_con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            postgre_cur = postgre_con.cursor()
            with open("prepare1.sql", "r") as f:
                postgre_cur.execute(f.read().format(POSTGRES_DATABASE))
                postgre_con.commit()
            postgre_cur.close()
            postgre_con.close()
        except Exception as e:
            pass

        postgre_con = psycopg2.connect(dbname=POSTGRES_DATABASE, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
        postgre_cur = postgre_con.cursor()
        with open("prepare2.sql", "r") as f:
            postgre_cur.execute(f.read())
            postgre_con.commit()
        postgre_cur.close()
        postgre_con.close()

        prepare_db = DB()
        prepare_db.redis_con.set("CURRENT_DATE", 0)
        prepare_db.redis_con.set("USE_MODERATION", 0)

        print("DB SETUP FINISHED")
        break
    except Exception as e:
        print("DB SETUP ERROR, RETRY")

app = FastAPI()

app.include_router(ads.router)
app.include_router(advertisers.router)
app.include_router(campaigns.router)
app.include_router(campaigns_img.router)
app.include_router(clients.router)
app.include_router(statistics.router)
app.include_router(time_.router)
app.include_router(moderation.router)
app.include_router(tgbot.router)

# run the app
if __name__ == "__main__":
    server_address = MAINAPI_HOST
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))