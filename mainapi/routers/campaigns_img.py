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

@router.put("/advertisers/{advertiserId}/campaigns/{campaignId}/image")
async def put_advertisers_advertiserId_campaigns_image(request:Request, response:Response, advertiserId:Optional[str]="", campaignId:Optional[str]="", image:Optional[UploadFile]=None):
    db = DB()

    try: 
        advertiserId = str(UUID(advertiserId))
        campaignId = str(UUID(campaignId))
        if image == None: raise Exception()
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_advertiser_exists(advertiserId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный рекламодатель не существует." }
    
    if not db.check_if_adv_camp_exists(advertiserId, campaignId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данное объявление не существует." }

    if image.size > IMAGES_MAXSIZE:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Размер изображения превышает лимит." }
    
    image_filetype = image.filename.split(".")[-1]

    if image_filetype not in IMAGES_FILETYPES:
        response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        return { "message": "Неверный формат изображения." }
    
    db.postgre_cur.execute("SELECT image FROM campaigns WHERE id=%s", (campaignId,))
    old_filename = db.postgre_cur.fetchone()["image"]

    if old_filename != None:
        os.remove(f"images/{old_filename}")

    new_filename = f"{campaignId}.{image_filetype}"

    async with aiofiles.open(f"images/{new_filename}", 'wb') as out_file:
        content = await image.read()
        await out_file.write(content)

    db.postgre_cur.execute("UPDATE campaigns SET image=%s WHERE id=%s", (new_filename, campaignId))
    db.postgre_con.commit()

    db.end()
    return {
        "image": new_filename
    }


@router.delete("/advertisers/{advertiserId}/campaigns/{campaignId}/image")
async def delete_advertisers_advertiserId_campaigns_image(request:Request, response:Response, advertiserId:Optional[str]="", campaignId:Optional[str]=""):
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


    db.postgre_cur.execute("SELECT image FROM campaigns WHERE id=%s", (campaignId,))
    old_filename = db.postgre_cur.fetchone()["image"]

    if old_filename == None:
        response.status_code = status.HTTP_403_FORBIDDEN
        return { "message": "У объявления не было изображения." }
    
    os.remove(f"images/{old_filename}")

    db.postgre_cur.execute("UPDATE campaigns SET image=%s WHERE id=%s", (None, campaignId))
    db.postgre_con.commit()

    db.end()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/images/{image}")
async def get_image(request:Request, response:Response, image:Optional[str]=None):
    # ../ и .. не работают - можно считать данную имплементацию безопасной.
    if not os.path.isfile(f"images/{image}"):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Изображение не найдено." }
    
    return FileResponse(f"images/{image}")