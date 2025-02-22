from fastapi import APIRouter, Request, Response, status
from typing import Annotated, Literal, List, Optional, Any
from uuid import UUID
from ..db import DB
from ..utils import *
from pydantic import BaseModel, RootModel
import psycopg2.errors

router = APIRouter()


class PostTimeAdvance(BaseModel):
    current_date: int

@router.post("/time/advance")
async def post_time_advance(request:Request, response:Response):
    db = DB()

    body = await request.json()
    try: PostTimeAdvance.model_validate(body)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    current_date = int(body["current_date"])

    db.redis_con.set("CURRENT_DATE", current_date)

    db.end()
    return {
        "current_date": db.get_current_date()
    }
