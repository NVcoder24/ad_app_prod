from fastapi import FastAPI, Request, Response, status
from cfg import *
import uvicorn
import http3

# create app
app = FastAPI()

@app.get("/")
async def ping(request:Request):
    return None

@app.post("/metrics")
async def metrics(request:Request):
    return [
        {
            "label": "Затрачено за последние N дней",
            "value": "spentall_lastn",
            "payloads": [
                {
                    "label": "Дней",
                    "name": "ndays",
                    "type": "input"
                }
            ]
        },
        {
            "label": "Показов и кликов за последние N дней",
            "value": "impr_lastn",
            "payloads": [
                {
                    "label": "Дней",
                    "name": "ndays",
                    "type": "input"
                }
            ]
        }
    ]

@app.post("/metric-payload-options")
async def metricspayloads():
    return []

@app.post("/query")
async def query(request:Request):
    body = await request.json()

    uuid = body["scopedVars"]["undefined"]["value"]

    client = http3.AsyncClient()

    resp = []

    for i in body["targets"]:
        # payload
        ndays = int(i["payload"]["ndays"])

        # get stats
        r = await client.get(f"http://{MAINAPI_HOST}/stats/advertisers/{uuid}/campaigns/daily")
        r_json = r.json()[::-1]

        # complite collumns
        columns = []
        if i["target"] == "spentall_lastn":
            columns = [
                {
                    "text": "День",
                    "type": "integer",
                },
                {
                    "text": "Потрачено всего",
                    "type": "number",
                },
                {
                    "text": "Потраччено на показы",
                    "type": "number",
                },
                {
                    "text": "Потрачено на переходы",
                    "type": "number"
                }
            ]
        if i["target"] == "impr_lastn":
            columns = [
                {
                    "text": "День",
                    "type": "integer",
                },
                {
                    "text": "Показы",
                    "type": "number",
                },
                {
                    "text": "Переходы",
                    "type": "number",
                }
            ]
        
        # compile data
        max_date = r_json[0]["date"]
        data = []
        for j in range(ndays):
            if j > len(r_json) - 1: break
            if max_date - r_json[j]["date"] < ndays:
                if i["target"] == "spentall_lastn":
                    data.append(
                        [
                            r_json[j]["date"],
                            r_json[j]["spent_total"],
                            r_json[j]["spent_impressions"],
                            r_json[j]["spent_clicks"]
                        ]
                    )
                if i["target"] == "impr_lastn":
                    data.append(
                        [
                            r_json[j]["date"],
                            r_json[j]["impressions_count"],
                            r_json[j]["clicks_count"]
                        ]
                    )

        # add to response
        resp.append({
            "type": "table",
            "columns": columns,
            "rows": data[::-1]
        })

    return resp

# run the app
if __name__ == "__main__":
    server_address = GRAFANA_API_HOST
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))