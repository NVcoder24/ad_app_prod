# ПЕРЕД ПУСКОМ НУЖНО СНЕСТИ БД!

from utils import *
import os
import random

PROTO = "http"
BASE_URL = "127.0.0.1:8080"
NAME = "Main API"

# Выключает ненужные принты
disable_logger_info(True)

# ==================
# post /clients/bulk
# ==================
test(METHOD_POST, f"{PROTO}://{BASE_URL}/clients/bulk", f"{NAME} - /clients/bulk - Без данных", expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/clients/bulk", f"{NAME} - /clients/bulk - Пустой массив", body=[], expected_body=[], expected_code=201)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/clients/bulk", f"{NAME} - /clients/bulk - Тест валидации 1", body=[
    {
        "client_id": "Это не uuid",
        "login": "test1",
        "age": 16,
        "location": "Moscow",
        "gender": "MALE"
    }
], expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/clients/bulk", f"{NAME} - /clients/bulk - Тест валидации 2", body=[
    {
        "client_id": get_random_uuid(),
        "login": "test1",
        "age": 16,
        "location": "Moscow",
        "gender": "TRANSGENDER"
    }
], expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/clients/bulk", f"{NAME} - /clients/bulk - Тест валидации 2", body=[
    {
        "client_id": get_random_uuid(),
        "age": 16,
        "location": "Moscow"
    }
], expected_code=400)

clients_data = [
    {
        "client_id": get_random_uuid(),
        "login": "test1",
        "age": 9,
        "location": "Moscow",
        "gender": "FEMALE"
    },
    {
        "client_id": get_random_uuid(),
        "login": "test2",
        "age": 18,
        "location": "Samara",
        "gender": "MALE"
    },
    {
        "client_id": get_random_uuid(),
        "login": "test3",
        "age": 26,
        "location": "Samara",
        "gender": "FEMALE"
    },
    {
        "client_id": get_random_uuid(),
        "login": "test4",
        "age": 67,
        "location": "Moscow",
        "gender": "MALE"
    }
]

test(METHOD_POST, f"{PROTO}://{BASE_URL}/clients/bulk", f"{NAME} - /clients/bulk - Верный запрос", body=clients_data, expected_body=clients_data, expected_code=201)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/clients/bulk", f"{NAME} - /clients/bulk - Загрузка существующего UUID", body=[clients_data[0]], expected_code=403)

# =====================
# get /clients/clientId
# =====================
test(METHOD_GET, f"{PROTO}://{BASE_URL}/clients/Не UUID", f"{NAME} - /clients/clientId - Тест валидации", expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/clients/{get_random_uuid()}", f"{NAME} - /clients/clientId - Не существующий UUID", expected_code=404)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/clients/{clients_data[0]['client_id']}", f"{NAME} - /clients/clientId - Пользователь test1", expected_body=clients_data[0], expected_code=200)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/clients/{clients_data[1]['client_id']}", f"{NAME} - /clients/clientId - Пользователь test2", expected_body=clients_data[1], expected_code=200)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/clients/{clients_data[2]['client_id']}", f"{NAME} - /clients/clientId - Пользователь test3", expected_body=clients_data[2], expected_code=200)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/clients/{clients_data[3]['client_id']}", f"{NAME} - /clients/clientId - Пользователь test4", expected_body=clients_data[3], expected_code=200)

# ======================
# post /advertisers/bulk
# ======================
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/bulk", f"{NAME} - /advertisers/bulk - Без данных", expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/bulk", f"{NAME} - /advertisers/bulk - Пустой массив", body=[], expected_code=201)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/bulk", f"{NAME} - /advertisers/bulk - Тест валидации 1", body=[
    {
        "advertiser_id": "Не UUID",
        "name": "test1"
    }
], expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/bulk", f"{NAME} - /advertisers/bulk - Тест валидации 2", body=[
    {
        "advertiser_id": get_random_uuid(),
    }
], expected_code=400)

adv_data = [
    {
        "advertiser_id": get_random_uuid(),
        "name": "test1"
    },
    {
        "advertiser_id": get_random_uuid(),
        "name": "test2"
    },
    {
        "advertiser_id": get_random_uuid(),
        "name": "test3"
    },
]

test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/bulk", f"{NAME} - /advertisers/bulk - Верный запрос", body=adv_data, expected_body=adv_data, expected_code=201)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/bulk", f"{NAME} - /advertisers/bulk - Загрузка существующего UUID", body=[adv_data[0]], expected_code=403)

# ===============================
# get /advertisers/{advertiserId}
# ===============================
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/Не UUID", f"{NAME} - /advertisers/advertiserId - Тест валидации", expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{get_random_uuid()}", f"{NAME} - /advertisers/advertiserId - Не существующий UUID", expected_code=404)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[0]["advertiser_id"]}", f"{NAME} - /advertisers/advertiserId - Получение test1", expected_body=adv_data[0], expected_code=200)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[1]["advertiser_id"]}", f"{NAME} - /advertisers/advertiserId - Получение test2", expected_body=adv_data[1], expected_code=200)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[2]["advertiser_id"]}", f"{NAME} - /advertisers/advertiserId - Получение test3", expected_body=adv_data[2], expected_code=200)

# ===============
# post /ml-scores
# ===============
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ml-scores", f"{NAME} - /ml-scores - Тест валидации 1", expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ml-scores", f"{NAME} - /ml-scores - Тест валидации 2", body={
    "client_id": "Не UUID",
    "advertiser_id": "Не UUID",
    "score": "Не число"
}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ml-scores", f"{NAME} - /ml-scores - Тест валидации 3", body={
    "client_id": get_random_uuid(),
}, expected_code=400)

ml_data = []
for i in clients_data:
    for j in adv_data:
        ml_data.append({
            "client_id": i["client_id"],
            "advertiser_id": j["advertiser_id"],
            "score": random.randint(0, 10000)
        })

for i in ml_data:
    test(METHOD_POST, f"{PROTO}://{BASE_URL}/ml-scores", f"{NAME} - /ml-scores - Верные данные", body=i, expected_code=200)

rnd_data = random.choice(ml_data)
rnd_data["score"] = random.randint(0, 10000)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ml-scores", f"{NAME} - /ml-scores - Обновление", body=rnd_data, expected_code=200)

# ==========================================
# post /advertisers/{advertiserId}/campaigns
# ==========================================
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{'Не UUID'}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации UUID", expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{get_random_uuid()}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Не существующий UUID", expected_code=404)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[0]["advertiser_id"]}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Без данных", expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[0]["advertiser_id"]}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации 1", body={}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[0]["advertiser_id"]}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации 2", body={
  "impressions_limit": "a",
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 0,
  "end_date": 0,
}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[0]["advertiser_id"]}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации 3", body={
  "impressions_limit": 0,
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 0,
  "end_date": 0,
  "targeting": {
    "gender": "TRANSGENDER",
  }
}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[0]["advertiser_id"]}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации 4", body={
  "impressions_limit": 0,
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 1,
  "end_date": 0,
}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{adv_data[0]["advertiser_id"]}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации 5", body={
  "impressions_limit": 0,
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 0,
  "end_date": 0,
  "targeting": {
    "gender": "MALE",
    "age_from": 50,
    "age_to": 20,
    "location": "Moscow"
  }
}, expected_code=400)
camp_data = {
    adv_data[0]["advertiser_id"]: [
        {
            "impressions_limit": 10,
            "clicks_limit": 10,
            "cost_per_impression": 2,
            "cost_per_click": 5.4,
            "ad_title": "Яндекс - найдётся всё!",
            "ad_text": "",
            "start_date": 0,
            "end_date": 10,
        },
        {
            "impressions_limit": 10,
            "clicks_limit": 10,
            "cost_per_impression": 2,
            "cost_per_click": 5.4,
            "ad_title": "Яндекс кидс - развлекательные видео",
            "ad_text": "",
            "start_date": 0,
            "end_date": 10,
            "targeting": {
                "gender": "ALL",
                "age_to": 12
            }
        }
    ],
    adv_data[1]["advertiser_id"]: [
        {
            "impressions_limit": 10,
            "clicks_limit": 10,
            "cost_per_impression": 2,
            "cost_per_click": 3.1,
            "ad_title": "Магазин оружия \"У ВАСИЛИЧА\"",
            "ad_text": "",
            "start_date": 0,
            "end_date": 10,
            "targeting": {
                "gender": "MALE",
                "age_from": 18,
                "location": "Samara"
            }
        }
    ],
    adv_data[2]["advertiser_id"]: [
        {
            "impressions_limit": 10,
            "clicks_limit": 10,
            "cost_per_impression": 2,
            "cost_per_click": 3.1,
            "ad_title": "Детский садик \"Веганский\"",
            "ad_text": "",
            "start_date": 0,
            "end_date": 10,
            "targeting": {
                "gender": "ALL",
                "location": "Moscow"
            }
        }
    ]
}

adv_ids = {

}

for i in camp_data:
    for j in camp_data[i]:
        test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{i}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Верные данные", body=j, expected_body=j, expected_code=201)
        returnbody = get_last_return_body()
        if returnbody["advertiser_id"] not in adv_ids.keys():
            adv_ids[returnbody["advertiser_id"]] = []
        adv_ids[returnbody["advertiser_id"]].append(returnbody["campaign_id"])

print("adv_ids = ", adv_ids)
print()

# =========================================
# get /advertisers/{advertiserId}/campaigns
# =========================================
advId = list(camp_data.keys())[0]
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{'Не UUID'}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации UUID", expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{get_random_uuid()}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Не существ UUID", expected_code=404)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации пагинации 1", query_params={"size": -3}, expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест валидации пагинации 2", query_params={"page": -3}, expected_code=400)
for i in camp_data:
    test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{i}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Верные данные 1", expected_body=camp_data[i], expected_code=200, valid_check_order=False)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Верные данные 1", expected_body=camp_data[advId], expected_code=200, valid_check_order=False)
lastbody = get_last_return_body()
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест пагинации 1", query_params={"size": 1}, expected_body=[camp_data[advId][0]], expected_code=200, valid_check_order=False)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест пагинации 2", query_params={"size": 1, "page": 1}, expected_body=[camp_data[advId][1]], expected_code=200, valid_check_order=False)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns - Тест пагинации 3", query_params={"size": 0}, expected_body=[], expected_code=200)

# ======================================================
# get /advertisers/{advertiserId}/campaigns/{campaignId}
# ======================================================
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{'Не UUID'}/campaigns/{'Не UUID'}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 1", expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{'Не UUID'}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 2", expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{'Не UUID'}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 3", expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{get_random_uuid()}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Не существ. UUID 1", expected_code=404)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{get_random_uuid()}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Не существ. UUID 2", expected_code=404)
for i in adv_ids:
    for j in range(len(adv_ids[i])):
        test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][j]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Верный запрос", expected_body=camp_data[advId][j], expected_code=200)

# ======================================================
# put /advertisers/{advertiserId}/campaigns/{campaignId}
# ======================================================
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{'Не UUID'}/campaigns/{'Не UUID'}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 1", expected_code=400)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{'Не UUID'}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 2", expected_code=400)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{'Не UUID'}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 3", expected_code=400)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{get_random_uuid()}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Не существ. UUID 1", expected_code=404)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{get_random_uuid()}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Не существ. UUID 2", expected_code=404)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации 1", body={
  "impressions_limit": "a",
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 0,
  "end_date": 0,
}, expected_code=400)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации 2", body={
  "impressions_limit": 0,
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 0,
  "end_date": 0,
  "targeting": {
    "gender": "TRANSGENDER",
  }
}, expected_code=400)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации 3", body={
  "impressions_limit": 0,
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 1,
  "end_date": 0,
}, expected_code=400)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации 4", body={
  "impressions_limit": 0,
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 0,
  "end_date": 0,
  "targeting": {
    "gender": "MALE",
    "age_from": 50,
    "age_to": 20,
    "location": "Moscow"
  }
}, expected_code=400)

test_body = camp_data[advId][1]
test_body_mod = test_body.copy()
test_body_mod["impressions_limit"] = 1
test_body_mod["clicks_limit"] = 2
test_body_mod["cost_per_impression"] = 3
test_body_mod["cost_per_click"] = 4
test_body_mod["ad_title"] = "тест тест"
test_body_mod["ad_text"] = "тест"
test_body_mod["start_date"] = 5
test_body_mod["end_date"] = 6
test_body_mod["targeting"]["gender"] = "MALE"
test_body_mod["targeting"]["age_from"] = 7
test_body_mod["targeting"]["age_to"] = 8
test_body_mod["targeting"]["location"] = "Samara"

test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][1]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Верный запрос 1", body=test_body_mod, expected_body=test_body_mod, expected_code=200)
test(METHOD_PUT, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][1]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Верный запрос 2", body=test_body, expected_body=test_body, expected_code=200)

# =========================================================
# delete /advertisers/{advertiserId}/campaigns/{campaignId}
# =========================================================
test(METHOD_DELETE, f"{PROTO}://{BASE_URL}/advertisers/{'Не UUID'}/campaigns/{'Не UUID'}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 1", expected_code=400)
test(METHOD_DELETE, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{'Не UUID'}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 2", expected_code=400)
test(METHOD_DELETE, f"{PROTO}://{BASE_URL}/advertisers/{'Не UUID'}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Тест валидации UUID 3", expected_code=400)
test(METHOD_DELETE, f"{PROTO}://{BASE_URL}/advertisers/{get_random_uuid()}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Не существ. UUID 1", expected_code=404)
test(METHOD_DELETE, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{get_random_uuid()}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Не существ. UUID 2", expected_code=404)
test(METHOD_DELETE, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Верные данные", expected_code=204)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns/{adv_ids[advId][0]}", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Проверка GET", expected_code=404)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/advertisers/{advId}/campaigns", f"{NAME} - /advertisers/advertiserId/campaigns/campaignId - Вернуть удалённое POST", body=camp_data[advId][0], expected_body=camp_data[advId][0], expected_code=201)
returnbody = get_last_return_body()
adv_ids[returnbody["advertiser_id"]][0] = returnbody["campaign_id"]

print("adv_ids = ", adv_ids)
print()

# ==================
# post /time/advance
# ==================
test(METHOD_POST, f"{PROTO}://{BASE_URL}/time/advance", f"{NAME} - /time/advance - Тест валидации 1", expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/time/advance", f"{NAME} - /time/advance - Тест валидации 2", body={}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/time/advance", f"{NAME} - /time/advance - Тест валидации 3", body={"current_date": "incorrect"}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/time/advance", f"{NAME} - /time/advance - Верные данные 1", body={"current_date": 0}, expected_body={"current_date": 0}, expected_code=200)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/time/advance", f"{NAME} - /time/advance - Верные данные 2", body={"current_date": 777}, expected_body={"current_date": 777}, expected_code=200)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/time/advance", f"{NAME} - /time/advance - Верные данные 3", body={"current_date": 0}, expected_body={"current_date": 0}, expected_code=200)

# ==================
# get /ads
# Более развёрнуторе
# тестирование в e2e
# ==================
test(METHOD_GET, f"{PROTO}://{BASE_URL}/ads", f"{NAME} - /ads - Тест валидации 1", expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/ads", f"{NAME} - /ads - Тест валидации 2", query_params={"client_id": ""}, expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/ads", f"{NAME} - /ads - Тест валидации 3", query_params={"client_id": "Не UUID"}, expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/ads", f"{NAME} - /ads - Не существ. UUID", query_params={"client_id": get_random_uuid()}, expected_code=404)

viewed1 = []
for i in clients_data:
    test(METHOD_GET, f"{PROTO}://{BASE_URL}/ads", f"{NAME} - /ads - Клиент {i}", query_params={"client_id": i["client_id"]}, expected_code=200)
    viewed1.append(get_last_return_body()["ad_id"])

test(METHOD_POST, f"{PROTO}://{BASE_URL}/time/advance", f"{NAME} - /ads - Меняем дату", body={"current_date": 1}, expected_body={"current_date": 1}, expected_code=200)

viewed2 = []
num = 0
for i in clients_data:
    test(METHOD_GET, f"{PROTO}://{BASE_URL}/ads", f"{NAME} - /ads - Клиент {i} (2)", query_params={"client_id": i["client_id"]}, expected_code=200)
    adId = get_last_return_body()["ad_id"]
    if viewed1[num] != adId:
        viewed2.append(adId)
    num += 1

print("viewed1 = ", viewed1)
print("viewed2 = ", viewed2)
print()

# ==================
# post /ads/{adId}/click
# Более развёрнуторе
# тестирование в e2e
# ==================
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ads/{'Не UUID'}/click", f"{NAME} - /ads/adId/click - Тест валидации 1", body={"client_id": clients_data[0]["client_id"]}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ads/{viewed2[0]}/click", f"{NAME} - /ads/adId/click - Тест валидации 2", body={"client_id": 'Не UUID'}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ads/{viewed2[0]}/click", f"{NAME} - /ads/adId/click - Тест валидации 3", body={}, expected_code=400)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ads/{get_random_uuid()}/click", f"{NAME} - /ads/adId/click - Не существ. UUID 1", body={"client_id": clients_data[0]["client_id"]}, expected_code=404)
test(METHOD_POST, f"{PROTO}://{BASE_URL}/ads/{viewed2[0]}/click", f"{NAME} - /ads/adId/click - Не существ. UUID 2", body={"client_id": get_random_uuid()}, expected_code=404)

for i in range(len(viewed1)):
    test(METHOD_POST, f"{PROTO}://{BASE_URL}/ads/{viewed1[i]}/click", f"{NAME} - /ads/adId/click - Клиент {i + 1}", body={"client_id": clients_data[i]["client_id"]}, expected_code=204)

# =================================
# get /stats/campaigns/{campaignId}
# Более развёрнуторе
# тестирование в e2e
# =================================
expected_stats_1 = {}
for i in adv_ids:
    for j in adv_ids[i]:
        expected_stats_1[j] = {
            "impressions_count": 0,
            "clicks_count": 0,
        }

for i in viewed1 + viewed2:
    expected_stats_1[i]["impressions_count"] += 1
for i in viewed1:
    expected_stats_1[i]["clicks_count"] += 1

test(METHOD_GET, f"{PROTO}://{BASE_URL}/stats/campaigns/{'Не UUID'}", f"{NAME} - /stats/campaigns/campaignId - Тест валидации 1", expected_code=400)
test(METHOD_GET, f"{PROTO}://{BASE_URL}/stats/campaigns/{get_random_uuid()}", f"{NAME} - /stats/campaigns/campaignId - Не существ. UUID", expected_code=404)

for i in expected_stats_1:
    test(METHOD_GET, f"{PROTO}://{BASE_URL}/stats/campaigns/{i}", f"{NAME} - /stats/campaigns/campaignId - Кампания 1", expected_body=expected_stats_1[i], expected_code=200)

# ===============================================
# get /stats/advertisers/{advertiserId}/campaigns
# Более развёрнуторе
# тестирование в e2e
# ===============================================
for i in adv_data:
    advId = i['advertiser_id']
    expected_data_1 = {
        "impressions_count": 0,
        "clicks_count": 0,
    }
    for j in viewed1 + viewed2:
        if j in adv_ids[advId]:
            expected_data_1["impressions_count"] += 1
    for j in viewed1:
        if j in adv_ids[advId]:
            expected_data_1["clicks_count"] += 1

    test(METHOD_GET, f"{PROTO}://{BASE_URL}/stats/advertisers/{advId}/campaigns", f"{NAME} - /stats/advertisers/advertiserId/campaigns - Рекламодатель {advId}", expected_body=expected_data_1, expected_code=200, valid_check_order=False)

# =======================================
# get /stats/campaigns/{campaignId}/daily
# Более развёрнуторе
# тестирование в e2e
# =======================================
expected_stats_2 = {}
for i in adv_ids:
    for j in adv_ids[i]:
        expected_stats_1[j] = []

def count_in_arr(a, v):
    r = 0
    for i in a:
        if i == v:
            r += 1
    return r

for j in expected_stats_2:
    if j in viewed2 or j in viewed1:
        expected_stats_2[j].append({
            "impressions_count": count_in_arr(viewed2, j),
            "clicks_count": count_in_arr(viewed1, j),
            "date": 1,
        })

for j in expected_stats_2:
    if j in viewed1:
        expected_stats_2[j].append({
            "impressions_count": count_in_arr(viewed1, j),
            "clicks_count": 0,
            "date": 0,
        })

for i in expected_stats_2:
    test(METHOD_GET, f"{PROTO}://{BASE_URL}/stats/campaigns/{i}/daily", f"{NAME} - /stats/campaigns/campaignId/daily - Кампания {i}", expected_body=expected_stats_2[i], expected_code=200)

# =====================================================
# get /stats/advertisers/{advertiserId}/campaigns/daily
# Более развёрнуторе
# тестирование в e2e
# =====================================================
for i in adv_data:
    advId = i['advertiser_id']
    expected_data_2 = []
    for j in viewed2 + viewed1:
        if j in adv_ids[advId]:
            expected_data_2.append(
                {
                    "impressions_count": count_in_arr(viewed2, j),
                    "clicks_count": count_in_arr(viewed1, j),
                    "date": 1,
                }
            )
            break
    for j in viewed1:
        if j in adv_ids[advId]:
            expected_data_2.append(
                {
                    "impressions_count": count_in_arr(viewed1, j),
                    "clicks_count": 0,
                    "date": 0,
                }
            )
            break

    test(METHOD_GET, f"{PROTO}://{BASE_URL}/stats/advertisers/{advId}/campaigns/daily", f"{NAME} - /stats/advertisers/advertiserId/campaigns/daily - Рекламодатель {advId}", expected_body=expected_data_2, expected_code=200, valid_check_order=False)

summary()