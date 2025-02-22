from fastapi import APIRouter, Request, Response, status
from typing import Annotated, Literal, List, Optional, Any
from uuid import UUID
from ..db import DB
from pydantic import BaseModel, RootModel
import psycopg2.errors

router = APIRouter()


@router.get("/ads")
async def get_ads(request:Request, response:Response, client_id:Optional[str]=""):
    db = DB()

    try: client_id = str(UUID(client_id))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_client_exists(client_id):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный клиент не существует." }

    current_date = db.get_current_date()

    db.postgre_cur.execute("SELECT * FROM clients WHERE id = %s LIMIT 1", (client_id,))
    client_data = db.postgre_cur.fetchone()

    # А вот и алгоритм показа
    db.postgre_cur.execute("""
                           -- Селектим всё только от таблицы с рекламами
                           SELECT campaigns.* FROM campaigns 
                           
                           -- Добавляем строке ML скор пары рекламодатель - клиент
                           LEFT JOIN mlscores on (mlscores.advertiser_id = campaigns.advertiser_id AND mlscores.client_id = %s) 

                           -- Добавляем строке показы этой рекламы пользователю
                           LEFT JOIN clicks on (clicks.campaign_id = campaigns.id AND clicks.client_id = %s)

                           -- Добавляем строке показы этой рекламы пользователю
                           LEFT JOIN impressions on (impressions.campaign_id = campaigns.id AND impressions.client_id = %s)
                           
                           -- Условия для рекламы
                           WHERE (
                           -- Условия активности рекламы
                           (SELECT COUNT(*) FROM impressions WHERE campaign_id = campaigns.id AND impressions.affects_stats = true) < impressions_limit AND
                           %s >= start_date AND %s <= end_date AND 
                           
                           -- Условия по таргету
                           (gender is NULL or gender LIKE %s or gender LIKE 'ALL') AND (age_from IS NULL or age_from <= %s) AND (age_to IS NULL or age_to >= %s) AND 
                           (location IS NULL or location LIKE %s) AND

                           -- Условия по модерации
                           is_moderated = true
                           ) 

                           -- Группировка по id рекламы
                           GROUP BY (campaigns.id, mlscores.score)

                           -- Сортировка
                           ORDER BY
                           -- Сортируем по кликам пользователя
                           COUNT(clicks.*) ASC,
                           -- Сортируем по показам пользователю
                           COUNT(impressions.*) ASC,
                           -- Сортируем по скору, если скора нет - считаем его за 0 
                           COALESCE(mlscores.score, 0) DESC 
                           
                           -- Нам нужно выдать только 1 рекламу, не будем мучать БД
                           LIMIT 1""",
                           (client_id, client_id, client_id, current_date, current_date, client_data["gender"], client_data["age"], client_data["age"], client_data["location"]))
    
    ad = db.postgre_cur.fetchone()

    if ad == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Нет подходящих объявлений." }

    resp = {
        "ad_id": ad["id"],
        "ad_title": ad["ad_title"],
        "ad_text": ad["ad_text"],
        "advertiser_id": ad["advertiser_id"],
    }

    if ad["image"] != None: resp["image"] = ad["image"]

    db.postgre_cur.execute("INSERT INTO impressions (campaign_id, date, client_id, cost, affects_stats) VALUES (%s, %s, %s, (SELECT cost_per_impression FROM campaigns WHERE id = %s), %s)", 
                            (ad["id"], current_date, client_id, ad["id"], not db.check_if_impression_exists(ad["id"], client_id)))
    db.postgre_con.commit()

    db.end()
    
    return resp


class PostAdsAdIdClick(BaseModel):
    client_id: UUID

@router.post("/ads/{adId}/click")
async def post_ads_adId_click(request:Request, response:Response, adId:Optional[str]=""):
    db = DB()

    try: adId = str(UUID(adId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    body = await request.json()
    try: PostAdsAdIdClick.model_validate(body)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_client_exists(body["client_id"]):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный клиент не существует." }
    
    if not db.check_if_campaign_exists(adId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данное объявление не существует." }

    # Не нужно лишних валидаций, если клиент увидел рекламу, значит может по ней кликнуть
    if not db.check_if_impression_exists(adId, body["client_id"]):
        response.status_code = status.HTTP_403_FORBIDDEN
        return { "message": "Данное объявление недоступно для данного клиента." }
    
    current_date = db.get_current_date()

    db.postgre_cur.execute("INSERT INTO clicks (campaign_id, date, client_id, cost, affects_stats) VALUES (%s, %s, %s, (SELECT cost_per_click FROM campaigns WHERE id = %s), %s)", 
                           (adId, current_date, body["client_id"], adId, not db.check_if_click_exists(adId, body["client_id"])))
    db.postgre_con.commit()

    db.end()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
