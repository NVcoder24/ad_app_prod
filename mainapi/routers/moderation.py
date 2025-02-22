from fastapi import APIRouter, Request, Response, status, File, UploadFile
from typing import Annotated, Literal, List, Optional, Any
from uuid import UUID
from ..db import DB
from ..cfg import *
from ..utils import *
from pydantic import BaseModel, RootModel
import psycopg2.errors
from fastapi.responses import FileResponse
import os.path
import aiofiles

router = APIRouter()

@router.post("/moderation/use_moderation/{state}")
async def moderation_use_moderation(state:bool):
    db = DB()
    db.set_use_moderation(state)
    db.end()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/moderation/results")
async def moderation_results(request:Request, response:Response):
    # интернал метод, валидация не требуется
    db = DB()

    body = await request.json()

    ad_id = body["ad_id"]
    is_good = body["is_good"]
    if is_good:
        print(f"Объявление {ad_id} прошло модерацию")
    else:
        message = body["message"]
        print(f"Объявление {ad_id} не прошло модерацию: {message}")

    db.postgre_cur.execute("UPDATE campaigns SET is_moderated=%s WHERE id=%s", (is_good, ad_id))
    db.postgre_con.commit()

    db.end()
    return Response(status_code=status.HTTP_204_NO_CONTENT)