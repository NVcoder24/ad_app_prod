from fastapi import APIRouter, Request, Response, status
from typing import Annotated, Literal, List, Optional
from uuid import UUID
from ..db import DB
from pydantic import BaseModel, RootModel
import psycopg2.errors

router = APIRouter()

class PostAdvertisersBulkItem(BaseModel):
    advertiser_id: UUID
    name: str

class PostAdvertisersBulk(RootModel):
    root: List[PostAdvertisersBulkItem]

@router.get("/advertisers/{advertiserId}")
async def get_advertisers_advertiserId(request:Request, response:Response, advertiserId:Optional[str]=""):
    db = DB()

    try: advertiserId = str(UUID(advertiserId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }

    db.postgre_cur.execute("SELECT * FROM advertisers WHERE id = %s LIMIT 1", (str(advertiserId),))
    result = db.postgre_cur.fetchone()

    resp = {
        "advertiser_id": result["id"],
        "name": result["name"],
    }

    db.end()
    return resp

@router.post("/advertisers/bulk")
async def post_advertisers_bulk(request:Request, response:Response):
    db = DB()

    body = await request.json()
    try: PostAdvertisersBulk.model_validate(body)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    for i in body:
        try:
            db.postgre_cur.execute("INSERT INTO advertisers (id, name) VALUES (%s, %s)", 
                                (i["advertiser_id"], i["name"]))
        except psycopg2.errors.UniqueViolation as e:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { "message": f"Рекламодатель {i['advertiser_id']} уже существует!" }
    
    db.postgre_con.commit()

    response.status_code = status.HTTP_201_CREATED

    db.end()
    return body

class PostMLScores(BaseModel):
    client_id: UUID
    advertiser_id: UUID
    score: int

@router.post("/ml-scores")
async def post_ml_scores(request:Request, response:Response):
    db = DB()

    body = await request.json()
    try: PostMLScores.model_validate(body)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_advertiser_exists(body["advertiser_id"]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Данный рекламодатель не существует." }
    
    if not db.check_if_client_exists(body["client_id"]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Данный клиент не существует." }

    db.postgre_cur.execute("SELECT COUNT(*) FROM mlscores WHERE client_id = %s AND advertiser_id = %s LIMIT 1",  (body["client_id"], body["advertiser_id"]))
    num = db.postgre_cur.fetchone()[0]

    if num > 0:
        db.postgre_cur.execute("UPDATE mlscores SET score = %s WHERE client_id = %s AND advertiser_id = %s", (body["score"], body["client_id"], body["advertiser_id"]))    
    else:
        db.postgre_cur.execute("INSERT INTO mlscores (client_id, advertiser_id, score) VALUES (%s, %s, %s)", (body["client_id"], body["advertiser_id"], body["score"]))
    db.postgre_con.commit()

    db.end()
    return Response(status_code=status.HTTP_200_OK)