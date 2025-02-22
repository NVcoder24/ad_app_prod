from fastapi import APIRouter, Request, Response, status
from typing import Annotated, Literal, List, Optional, Any
from uuid import UUID
from ..db import DB
from ..utils import *
from pydantic import BaseModel, RootModel
import psycopg2.errors
import os

router = APIRouter()

class PostAdvAdvIdCampaignsTargeting(BaseModel):
    gender: Optional[Literal["MALE", "FEMALE", "ALL"]] = None
    age_from: Optional[int] = None
    age_to: Optional[int] = None
    location: Optional[str] = None

class PostAdvAdvIdCampaigns(BaseModel):
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    start_date: int
    end_date: int
    targeting: Optional[Any] = None

@router.post("/advertisers/{advertiserId}/campaigns")
async def post_advertisers_advertiserId_campaigns(request:Request, response:Response, advertiserId:Optional[str]=""):
    db = DB()

    try: advertiserId = str(UUID(advertiserId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }
    
    body = await request.json()
    try: PostAdvAdvIdCampaigns.model_validate(body)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if "targeting" not in body.keys():
        body["targeting"] = {}
    else:
        try: PostAdvAdvIdCampaignsTargeting.model_validate(body["targeting"])
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "message": "Неверный формат запроса." }

        age_from = dict_get_or_none(body["targeting"], "age_from")
        age_to = dict_get_or_none(body["targeting"], "age_to")

        if age_from != None and age_to != None:
            if age_from > age_to:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return { "message": "Неверный формат запроса." }

    if body["start_date"] > body["end_date"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    use_moderation = db.get_use_moderation()

    db.postgre_cur.execute("""INSERT INTO campaigns (impressions_limit, clicks_limit, cost_per_impression, cost_per_click, ad_title, 
                           ad_text, start_date, end_date, gender, age_from, age_to, location, advertiser_id) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                           (body["impressions_limit"], body["clicks_limit"], body["cost_per_impression"], body["cost_per_click"], 
                            body["ad_title"], body["ad_text"], body["start_date"], body["end_date"], dict_get_or_none(body["targeting"], "gender"), 
                            dict_get_or_none(body["targeting"], "age_from"), dict_get_or_none(body["targeting"], "age_to"), dict_get_or_none(body["targeting"], "location"), 
                            advertiserId))
    inserted_id = db.postgre_cur.fetchone()["id"]
    if use_moderation:
        db.postgre_cur.execute("UPDATE campaigns SET is_moderated=NULL WHERE id=%s", (inserted_id,))
    db.postgre_con.commit()

    if use_moderation:
        await schedule_moderation(inserted_id, body["ad_title"], body["ad_text"])
        print(f"scheduled moderation for {inserted_id}")

    db.postgre_cur.execute("SELECT * FROM campaigns WHERE advertiser_id = %s AND id = %s LIMIT 1", (advertiserId, inserted_id))
    result = db.postgre_cur.fetchone()

    response.status_code = status.HTTP_201_CREATED

    db.end()
    return format_campaign(result)


@router.get("/advertisers/{advertiserId}/campaigns")
async def get_advertisers_advertiserId_campaigns(request:Request, response:Response, advertiserId:Optional[str]="", size: Optional[Any] = None, page: Optional[Any] = None):
    db = DB()

    try: 
        advertiserId = str(UUID(advertiserId))
        if size != None: size = int(size)
        if page != None: page = int(page)
        if size != None and size < 0: raise Exception()
        if page != None and page < 0: raise Exception()
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }

    query = "SELECT * FROM campaigns WHERE advertiser_id = %s"
    args = [advertiserId]
    if size != None:
        query += " LIMIT %s"
        args.append(size)
    if page != None:
        query += " OFFSET %s"
        args.append(size * page)

    db.postgre_cur.execute(query, args)

    result = db.postgre_cur.fetchall()

    resp = [ format_campaign(i) for i in result ]

    db.end()
    return resp


@router.get("/advertisers/{advertiserId}/campaigns/{campaignId}")
async def get_advertisers_advertiserId_campaigns_campaignId(request:Request, response:Response, advertiserId:Optional[str]="", campaignId:Optional[str]=""):
    db = DB()

    try: 
        advertiserId = str(UUID(advertiserId))
        campaignId = str(UUID(campaignId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }
    
    if not db.check_if_adv_camp_exists(advertiserId, campaignId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данное объявление не существует." }

    db.postgre_cur.execute("SELECT * FROM campaigns WHERE advertiser_id = %s AND id = %s LIMIT 1", (advertiserId, campaignId))

    result = db.postgre_cur.fetchone()

    db.end()
    return format_campaign(result)


@router.put("/advertisers/{advertiserId}/campaigns/{campaignId}")
async def put_advertisers_advertiserId_campaigns_campaignId(request:Request, response:Response, advertiserId:Optional[str]="", campaignId:Optional[str]=""):
    db = DB()

    try: 
        advertiserId = str(UUID(advertiserId))
        campaignId = str(UUID(campaignId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }
    
    if not db.check_if_adv_camp_exists(advertiserId, campaignId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данное объявление не существует." }

    body = await request.json()
    try: PostAdvAdvIdCampaigns.model_validate(body)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if "targeting" not in body.keys():
        body["targeting"] = {}
    else:
        try: PostAdvAdvIdCampaignsTargeting.model_validate(body["targeting"])
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "message": "Неверный формат запроса." }

        age_from = dict_get_or_none(body["targeting"], "age_from")
        age_to = dict_get_or_none(body["targeting"], "age_to")

        if age_from != None and age_to != None:
            if age_from > age_to:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return { "message": "Неверный формат запроса." }

    if body["start_date"] > body["end_date"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    keys = [
        "impressions_limit",
        "clicks_limit",
        "cost_per_impression",
        "cost_per_click",
        "ad_title",
        "ad_text",
        "start_date",
        "end_date"
    ]

    target_keys = [
        "gender",
        "age_from",
        "age_to",
        "location"
    ]

    use_moderation = db.get_use_moderation()

    if use_moderation:
        db.postgre_cur.execute("SELECT ad_title, ad_text FROM campaigns WHERE id=%s", (campaignId,))
        old_texts = db.postgre_cur.fetchone()

    for i in keys:
        if body[i] != None:
            db.postgre_cur.execute(f"UPDATE campaigns SET {i} = %s WHERE advertiser_id = %s AND id = %s", (body[i], advertiserId, campaignId))
    for i in target_keys:
        db.postgre_cur.execute(f"UPDATE campaigns SET {i} = %s WHERE advertiser_id = %s AND id = %s", (dict_get_or_none(body["targeting"], i), advertiserId, campaignId))
    if use_moderation:
        # если тексты не поменялись, не нужно отправлять на модерацию
        if body["ad_title"] != old_texts["ad_title"] or body["ad_text"] != old_texts["ad_text"]:
            db.postgre_cur.execute("UPDATE campaigns SET is_moderated=NULL WHERE id=%s", (campaignId,))
    db.postgre_con.commit()

    if use_moderation:
        await schedule_moderation(campaignId, body["ad_title"], body["ad_text"])
    
    db.postgre_cur.execute("SELECT * FROM campaigns WHERE advertiser_id = %s AND id = %s LIMIT 1", (advertiserId, campaignId))
    result = db.postgre_cur.fetchone()

    db.end()
    return format_campaign(result)


@router.delete("/advertisers/{advertiserId}/campaigns/{campaignId}")
async def delete_advertisers_advertiserId_campaigns_campaignId(request:Request, response:Response, advertiserId:Optional[str]="", campaignId:Optional[str]=""):
    db = DB()

    try: 
        advertiserId = str(UUID(advertiserId))
        campaignId = str(UUID(campaignId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }
    
    if not db.check_if_adv_camp_exists(advertiserId, campaignId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данное объявление не существует." }

    # Не забываем удалить изображение, если есть
    db.postgre_cur.execute("SELECT image FROM campaigns WHERE id=%s", (campaignId,))
    old_filename = db.postgre_cur.fetchone()["image"]
    if old_filename != None:
        os.remove(f"images/{old_filename}")
    # Удаляем кампанию
    db.postgre_cur.execute("DELETE FROM campaigns WHERE advertiser_id = %s AND id = %s", (advertiserId, campaignId))
    # Почистить статистику
    db.postgre_cur.execute("DELETE FROM impressions WHERE campaign_id = %s", (campaignId,))
    db.postgre_cur.execute("DELETE FROM clicks WHERE campaign_id = %s", (campaignId,))
    db.postgre_con.commit()

    db.end()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
