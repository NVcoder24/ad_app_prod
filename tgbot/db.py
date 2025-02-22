import redis
from cfg import *

class DB:
    def __init__(self):
        self.redis_con = redis.Redis(host=TGBOT_REDIS_HOST, port=TGBOT_REDIS_PORT, db=TGBOT_REDIS_DB)
    
    def end(self):
        self.redis_con.close()
