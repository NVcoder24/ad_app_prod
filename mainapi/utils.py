from .cfg import *
import http3
from .db import DB

def dict_get_or_none(d:dict, k):
    if k in d.keys():
        return d[k]
    else:
        return None
    
def format_campaign(i):
    item = {
        "campaign_id": i["id"],
        "advertiser_id": i["advertiser_id"],
        "impressions_limit": i["impressions_limit"],
        "clicks_limit": i["clicks_limit"],
        "cost_per_impression": i["cost_per_impression"],
        "cost_per_click": i["cost_per_click"],
        "ad_title": i["ad_title"],
        "ad_text": i["ad_text"],
        "start_date": i["start_date"],
        "end_date": i["end_date"],
        "targeting": {}
    }

    if i["gender"] != None: item["targeting"]["gender"] = i["gender"]
    if i["age_from"] != None: item["targeting"]["age_from"] = i["age_from"]
    if i["age_to"] != None: item["targeting"]["age_to"] = i["age_to"]
    if i["location"] != None: item["targeting"]["location"] = i["location"]
    
    if i["image"] != None: item["image"] = i["image"]
    
    db = DB()
    
    if db.get_use_moderation():
        if i["is_moderated"] == None: item["moderation_status"] = "pending"
        elif i["is_moderated"] == False: item["moderation_status"] = "failed"
        else: item["moderation_status"] = "succesful"

    return item

async def schedule_moderation(ad_id, ad_title, ad_text):
    print(f"Отправка объявления {ad_id} на модерацию")
    client = http3.AsyncClient()
    try:
        r = await client.post(f"http://{MODERATION_HOST}/schedule/", json={
            "ad_id": ad_id,
            "ad_title": ad_title,
            "ad_text": ad_text
        }, timeout=3)
        if r.status_code != 200: Exception("status code not 200!")
    except Exception as e:
        # иммитируем получение ответа от сервиса
        await client.post(f"http://{MAINAPI_HOST}/moderation/results", json={
            "ad_id": ad_id,
            "is_good": False,
            "message": "Не удалось отправить объявление на модерацию."
        })
        print(f"Ошибка модерации: {e}")