from fastapi import APIRouter, Request, Response, status
from typing import Annotated, Literal, List, Optional
from uuid import UUID
from ..db import DB
from pydantic import BaseModel, RootModel
import psycopg2.errors

router = APIRouter()

@router.get("/clients/{clientId}")
async def get_clients_clientId(request:Request, response:Response, clientId:Optional[str]=""):
    db = DB()

    try: clientId = str(UUID(clientId))
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    if not db.check_if_client_exists(clientId):
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "message": "Данный клиент не существует." }

    db.postgre_cur.execute("SELECT * FROM clients WHERE id = %s LIMIT 1", (str(clientId),))
    result = db.postgre_cur.fetchone()

    resp = {
        "client_id": result["id"],
        "login": result["login"],
        "age": result["age"],
        "location": result["location"],
        "gender": result["gender"],
    }

    db.end()
    return resp

class PostClientsBulkItem(BaseModel):
    client_id: UUID
    login: str
    age: int
    location: str
    gender: Literal["MALE", "FEMALE"]

class PostClientsBulk(RootModel):
    root: List[PostClientsBulkItem]

@router.post("/clients/bulk")
async def post_clients_bulk(request:Request, response:Response):    
    db = DB()

    body = await request.json()
    try: PostClientsBulk.model_validate(body)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }

    for i in body:
        try:
            db.postgre_cur.execute("INSERT INTO clients (id, login, age, location, gender) VALUES (%s, %s, %s, %s, %s)", 
                                (i["client_id"], i["login"], i["age"], i["location"], i["gender"]))
        except psycopg2.errors.UniqueViolation as e:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { "message": f"Пользователь {i['client_id']} уже существует!" }
    
    db.postgre_con.commit()

    response.status_code = status.HTTP_201_CREATED

    db.end()
    return body