from pydantic import BaseModel
from fastapi import FastAPI, Request, Response, status
from cfg import *
import uvicorn
import http3

# create app
app = FastAPI()

class GetGenerateText(BaseModel):
    ad_title: str

@app.get("/generate_text")
async def generate_text(request:Request, response:Response):
    body = await request.json()
    try: GetGenerateText.model_validate(body)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Неверный формат запроса." }
    
    prompt = {
        "modelUri": f"gpt://{YAGPT_CATALOG}/yandexgpt-lite/rc",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": "1000",
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты - генератор текстов для рекламных объявлений. Твоя задача - по предоставленному заголовку объявления, предоставить наиболее продающий и в то же время короткий текст объявления. Не используй язык разметки."
            },
            {
                "role": "user",
                "text": body["ad_title"]
            }
        ]
    }

    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YAGPT_KEY}"
    }

    client = http3.AsyncClient()
    r = await client.post(url, headers=headers, json=prompt, timeout=120, verify=False)
    if r.status_code != 200:
        response.status_code = status.HTTP_400_BAD_REQUEST
        print(r.text)
        return { "message": "Не удалось сгенерировать текст." }
    r_json = r.json()
    return {
        "ad_text": r_json["result"]["alternatives"][0]["message"]["text"]
    }

# run the app
if __name__ == "__main__":
    server_address = LLM_API_HOST
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))