from fastapi import APIRouter, Request, Response, status, File, UploadFile
from typing import Annotated, Literal, List, Optional, Any
from uuid import UUID
from ..db import DB
from ..cfg import *
from ..utils import *
from pydantic import BaseModel, RootModel
from fastapi.responses import FileResponse
import os.path
import aiofiles

router = APIRouter()

@router.get("/tgbot/check_if_adv_exists/{adv_id}")
async def adv_id_exists(request:Request, response:Response, adv_id:Optional[str]=""):
    # интернал метод, валидация не требуется
    db = DB()

    exists = db.check_if_advertiser_exists(adv_id)
    name = ""

    if exists:
        db.postgre_cur.execute("SELECT name FROM advertisers WHERE id=%s", (adv_id,))
        name = db.postgre_cur.fetchone()["name"]

    resp = {
        "exists": exists,
        "name": name
    }

    db.end()
    return resp