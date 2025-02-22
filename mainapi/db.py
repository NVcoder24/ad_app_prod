import psycopg2
import psycopg2.extras
import redis
from .cfg import *

class DB:
    def __init__(self):
        self.postgre_con = psycopg2.connect(dbname=POSTGRES_DATABASE, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
        self.postgre_cur = self.postgre_con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.redis_con = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    
    def end(self):
        self.postgre_cur.close()
        self.postgre_con.close()
        self.redis_con.close()

    def get_current_date(self):
        return int(self.redis_con.get("CURRENT_DATE").decode())
    
    def check_if_client_exists(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM clients WHERE id = %s LIMIT 1", (uuid,))
        return self.postgre_cur.fetchone()[0] > 0
    
    def check_if_advertiser_exists(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM advertisers WHERE id = %s LIMIT 1", (uuid,))
        return self.postgre_cur.fetchone()[0] > 0
    
    def check_if_campaign_exists(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM campaigns WHERE id = %s LIMIT 1", (uuid,))
        return self.postgre_cur.fetchone()[0] > 0
    
    def check_if_adv_camp_exists(self, adv_id, ad_id):
        self.postgre_cur.execute("SELECT COUNT(*) FROM campaigns WHERE advertiser_id = %s AND id = %s LIMIT 1", (adv_id,ad_id))
        return self.postgre_cur.fetchone()[0] > 0

    def check_if_campaign_active(self, uuid):
        current_date = self.get_current_date()

        self.postgre_cur.execute("""SELECT COUNT(*) FROM campaigns WHERE
                                 
                                  -- Условия активности рекламы
                                 ((SELECT COUNT(*) FROM impressions WHERE campaign_id = campaigns.id) < impressions_limit AND 
                                 %s >= start_date AND %s <= end_date)
                                 
                                 AND id = %s
                                 
                                 LIMIT 1""", (current_date, current_date, uuid))
        return self.postgre_cur.fetchone()[0] > 0
    
    def check_if_campaign_active_for_click(self, uuid):
        current_date = self.get_current_date()

        self.postgre_cur.execute("SELECT COUNT(*) FROM impressions WHERE campaign_id = %s", (uuid,))
        clicks = self.postgre_cur.fetchone()[0]

        self.postgre_cur.execute("""SELECT COUNT(*) FROM campaigns WHERE
                                 
                                  -- Условия активности рекламы (для клика)
                                 %s < clicks_limit AND 
                                 -- Кликов не должно быть больше просмотров
                                 %s < (SELECT COUNT(*) FROM impressions WHERE campaign_id = campaigns.id) AND
                                 %s >= start_date AND %s <= end_date
                                 
                                 AND id = %s
                                 
                                 LIMIT 1""", (clicks, clicks, current_date, current_date, uuid))
        return self.postgre_cur.fetchone()[0] > 0
    
    def check_if_campaign_active_for_user(self, uuid, client_id):
        self.postgre_cur.execute("SELECT * FROM clients WHERE id = %s LIMIT 1", (client_id,))
        client_data = self.postgre_cur.fetchone()

        self.postgre_cur.execute("""SELECT COUNT(*) FROM campaigns WHERE
                                 
                                 -- Условия по таргету
                                 ((gender is NULL or gender LIKE %s or gender LIKE 'ALL') AND (age_from IS NULL or age_from <= %s) AND (age_to IS NULL or age_to >= %s) AND 
                                 (location IS NULL or location LIKE %s))
                                 
                                 AND id = %s
                                 
                                 LIMIT 1""",
                                 (client_data["gender"], client_data["age"], client_data["age"], client_data["location"], uuid))
        return self.postgre_cur.fetchone()[0] > 0

    def check_if_impression_exists(self, uuid, client_id):
        self.postgre_cur.execute("SELECT COUNT(*) FROM impressions WHERE campaign_id = %s AND client_id = %s LIMIT 1", (uuid, client_id))
        return self.postgre_cur.fetchone()[0] > 0

    def check_if_click_exists(self, uuid, client_id):
        self.postgre_cur.execute("SELECT COUNT(*) FROM clicks WHERE campaign_id = %s AND client_id = %s LIMIT 1", (uuid, client_id))
        return self.postgre_cur.fetchone()[0] > 0

    def get_stats(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM impressions WHERE campaign_id = %s AND affects_stats = true", (uuid,))
        impressions = self.postgre_cur.fetchone()[0]
        self.postgre_cur.execute("SELECT COUNT(*) FROM clicks WHERE campaign_id = %s AND affects_stats = true", (uuid,))
        clicks = self.postgre_cur.fetchone()[0]

        self.postgre_cur.execute("SELECT GREATEST(SUM(cost), 0) FROM impressions WHERE campaign_id = %s AND affects_stats = true", (uuid,))
        spent_impressions = self.postgre_cur.fetchone()[0]
        self.postgre_cur.execute("SELECT GREATEST(SUM(cost), 0) FROM clicks WHERE campaign_id = %s AND affects_stats = true", (uuid,))
        spent_clicks = self.postgre_cur.fetchone()[0]

        return {
            "impressions": impressions,
            "clicks": clicks,
            "spent_impressions": spent_impressions,
            "spent_clicks": spent_clicks
        }
    
    def get_stats_for_date(self, uuid, date):
        self.postgre_cur.execute("SELECT COUNT(*) FROM impressions WHERE campaign_id = %s AND date = %s AND affects_stats = true", (uuid, date))
        impressions = self.postgre_cur.fetchone()[0]
        self.postgre_cur.execute("SELECT COUNT(*) FROM clicks WHERE campaign_id = %s AND date = %s AND affects_stats = true", (uuid, date))
        clicks = self.postgre_cur.fetchone()[0]

        self.postgre_cur.execute("SELECT GREATEST(SUM(cost), 0) FROM impressions WHERE campaign_id = %s AND date = %s AND affects_stats = true", (uuid, date))
        spent_impressions = self.postgre_cur.fetchone()[0]
        self.postgre_cur.execute("SELECT GREATEST(SUM(cost), 0) FROM clicks WHERE campaign_id = %s AND date = %s AND affects_stats = true", (uuid, date))
        spent_clicks = self.postgre_cur.fetchone()[0]

        return {
            "impressions": impressions,
            "clicks": clicks,
            "spent_impressions": spent_impressions,
            "spent_clicks": spent_clicks
        }
    
    def get_unique_stats_dates(self, uuid):
        self.postgre_cur.execute("SELECT DISTINCT date FROM impressions WHERE campaign_id = %s AND affects_stats = true", (uuid,))
        dates_impressions = [ i[0] for i in self.postgre_cur.fetchall() ]
        self.postgre_cur.execute("SELECT DISTINCT date FROM clicks WHERE campaign_id = %s AND affects_stats = true", (uuid,))
        dates_clicks = [ i[0] for i in self.postgre_cur.fetchall() ]
        return list(set(dates_impressions + dates_clicks))

    def get_use_moderation(self):
        return self.redis_con.get("USE_MODERATION").decode() == "1"
    
    def set_use_moderation(self, use_moderation:bool):
        return self.redis_con.set("USE_MODERATION", 1 if use_moderation else 0)