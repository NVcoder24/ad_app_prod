from fastapi import APIRouter, Request, Response, status
from typing import Annotated, Literal, List, Optional, Any
from uuid import UUID
from ..db import DB
from pydantic import BaseModel, RootModel
import psycopg2.errors

router = APIRouter()


# DRY покинул чат :)

@router.get("/stats/campaigns/{campaignId}")
async def get_stats_campaigns_campaignId(request:Request, response:Response, campaignId:Optional[str]=""):
    db = DB()

    try: campaignId = str(UUID(campaignId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }
    
    if not db.check_if_campaign_exists(campaignId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данное объявление не существует." }

    statistics = db.get_stats(campaignId)

    conversion = 0
    if statistics["impressions"] > 0:
        conversion = statistics["clicks"] / statistics["impressions"] * 100
    spent_total = statistics["spent_impressions"] + statistics["spent_clicks"]

    db.end()
    return {
        "impressions_count": statistics["impressions"],
        "clicks_count": statistics["clicks"],
        "conversion": conversion,
        "spent_impressions": statistics["spent_impressions"],
        "spent_clicks": statistics["spent_clicks"],
        "spent_total": spent_total
    }


@router.get("/stats/advertisers/{advertiserId}/campaigns")
async def get_stats_advertisers_advertiserId(request:Request, response:Response, advertiserId:Optional[str]=""):
    db = DB()

    try: advertiserId = str(UUID(advertiserId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }
    
    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }
    
    all_impressions = 0
    all_clicks = 0
    all_spent_impressions = 0
    all_spent_clicks = 0

    db.postgre_cur.execute("SELECT id FROM campaigns WHERE advertiser_id = %s", (advertiserId,))
    ids = [ i[0] for i in db.postgre_cur.fetchall() ]

    for campaignId in ids:
        statistics = db.get_stats(campaignId)

        all_impressions += statistics["impressions"]
        all_clicks += statistics["clicks"]
        all_spent_impressions += statistics["spent_impressions"]
        all_spent_clicks += statistics["spent_clicks"]

    conversion = 0
    if all_impressions > 0:
        conversion = all_clicks / all_impressions * 100
    spent_total = all_spent_impressions + all_spent_clicks

    db.end()
    return {
        "impressions_count": all_impressions,
        "clicks_count": all_clicks,
        "conversion": conversion,
        "spent_impressions": all_spent_impressions,
        "spent_clicks": all_spent_clicks,
        "spent_total": spent_total
    }


@router.get("/stats/campaigns/{campaignId}/daily")
async def get_stats_campaigns_campaignId_daily(request:Request, response:Response, campaignId:Optional[str]=""):
    db = DB()

    try: campaignId = str(UUID(campaignId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }
    
    if not db.check_if_campaign_exists(campaignId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данное объявление не существует." }

    resp = []

    for i in db.get_unique_stats_dates(campaignId):
        statistics = db.get_stats_for_date(campaignId, i)

        conversion = 0
        if statistics["impressions"] > 0:
            conversion = statistics["clicks"] / statistics["impressions"] * 100
        spent_total = statistics["spent_impressions"] + statistics["spent_clicks"]

        resp.append({
            "impressions_count": statistics["impressions"],
            "clicks_count": statistics["clicks"],
            "conversion": conversion,
            "spent_impressions": statistics["spent_impressions"],
            "spent_clicks": statistics["spent_clicks"],
            "spent_total": spent_total,
            "date": i
        })

    db.end()
    return resp


@router.get("/stats/advertisers/{advertiserId}/campaigns/daily")
async def get_stats_advertisers_advertiserId_daily(request:Request, response:Response, advertiserId:Optional[str]=""):
    db = DB()

    try: advertiserId = str(UUID(advertiserId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }
    
    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }
    
    resp = []

    alldates = []

    db.postgre_cur.execute("SELECT id FROM campaigns WHERE advertiser_id = %s", (advertiserId,))
    ids = [ i[0] for i in db.postgre_cur.fetchall() ]

    for i in ids:
        alldates += db.get_unique_stats_dates(i)

    dates = list(set(alldates))

    for i in dates:
        all_impressions = 0
        all_clicks = 0
        all_spent_impressions = 0
        all_spent_clicks = 0

        for campaignId in ids:
            statistics = db.get_stats_for_date(campaignId, i)

            all_impressions += statistics["impressions"]
            all_clicks += statistics["clicks"]
            all_spent_impressions += statistics["spent_impressions"]
            all_spent_clicks += statistics["spent_clicks"]

        conversion = 0
        if all_impressions > 0:
            conversion = all_clicks / all_impressions * 100
        spent_total = all_spent_impressions + all_spent_clicks

        resp.append({
            "impressions_count": all_impressions,
            "clicks_count": all_clicks,
            "conversion": conversion,
            "spent_impressions": all_spent_impressions,
            "spent_clicks": all_spent_clicks,
            "spent_total": spent_total,
            "date": i
        })

    db.end()
    return resp
