import asyncio
from aiogram import Bot, Dispatcher, methods, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from uuid import UUID
from db import DB
from cfg import *
import http3

dp = Dispatcher()
bot = Bot(token=TGBOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

def check_user_auth(user_id):
    db = DB()
    try:
        get_adv_id(user_id)
        result = True
    except Exception as e:
        result = False
    db.end()
    return result

def get_adv_id(user_id):
    db = DB()
    adv_id = db.redis_con.get(f"tgbot_auth_{user_id}").decode()
    db.end()
    return adv_id

def get_state_for_user(user_id):
    db = DB()
    try:
        result = db.redis_con.get(f"tgbot_state_{user_id}").decode()
    except Exception as e:
        result = None
    db.end()
    return result

def set_state_for_user(user_id, state):
    db = DB()
    try:
        if state == None:
            db.redis_con.delete(f"tgbot_state_{user_id}")
        else:
            db.redis_con.set(f"tgbot_state_{user_id}", state)
    except Exception as e:
        pass
    db.end()

def user_delete_all_temp(user_id):
    db = DB()
    for key in db.redis_con.scan_iter(f"tgbot_temp_{user_id}_*"):
        db.redis_con.delete(key)
    db.end()

def user_temp_set(user_id, key, val):
    db = DB()
    db.redis_con.set(f"tgbot_temp_{user_id}_{key}", val)
    db.end()

def user_temp_get(user_id, key):
    db = DB()
    try:
        result = db.redis_con.get(f"tgbot_temp_{user_id}_{key}").decode()
    except Exception as e:
        result = None
    db.end()
    return result

default_kb_arr = [
    [types.KeyboardButton(text="Создать объявление", ), types.KeyboardButton(text="Просмотреть объявления")],
    [types.KeyboardButton(text="Просмотреть статистику по всем объявлениям")],
    [types.KeyboardButton(text="Выйти из профиля")],
]
default_kb = types.ReplyKeyboardMarkup(keyboard=default_kb_arr, resize_keyboard=True)

cancel_kb_arr = [
    [types.KeyboardButton(text="❌ Отмена")]
]
cancel_kb = types.ReplyKeyboardMarkup(keyboard=cancel_kb_arr, resize_keyboard=True)

no_kb = types.ReplyKeyboardRemove()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if not check_user_auth(message.from_user.id):
        await message.answer(f"Здравствуйте, пожалуйста, введите свой UUID.", reply_markup=no_kb)
    else:
        await message.answer(f"Привет, давно не виделись 😁", reply_markup=default_kb)

@dp.message()
async def on_message(message: Message) -> None:
    client = http3.AsyncClient()

    if not check_user_auth(message.from_user.id):
        # валидируем UUID
        try:
            adv_uuid = str(UUID(message.text))
        except Exception as e:
            await message.answer(f"Это не UUID.", reply_markup=no_kb)
            return

        # Проверяем, существует ли такой рекламодатель
        await message.answer("Идёт авторизация...", reply_markup=no_kb)
        r = await client.get(f"http://{MAINAPI_HOST}/tgbot/check_if_adv_exists/{adv_uuid}")
        r_json = r.json()
        adv_uuid_exists = r_json["exists"]

        if adv_uuid_exists:
            # Существует
            db = DB()
            db.redis_con.set(f"tgbot_auth_{message.from_user.id}", adv_uuid)
            db.end()
            set_state_for_user(message.from_user.id, None)
            user_delete_all_temp(message.from_user.id)
            await message.answer(f"Вы авторизовались, как {r_json["name"]}!", parse_mode=ParseMode.HTML, reply_markup=default_kb)
        else:
            # Не существует
            await message.answer("Такого рекламодателя не существует!", reply_markup=no_kb)
        return

    user_id = message.from_user.id
    user_state = get_state_for_user(user_id)

    # Отмена
    if message.text == "❌ Отмена":
        await message.answer("Отменено.", reply_markup=default_kb)
        set_state_for_user(user_id, None)
        user_delete_all_temp(user_id)
        return

    # Создание объявления
    if message.text == "Создать объявление" and user_state == None:
        await message.answer("Введите заголовок объявления", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in0")
        return
    if user_state == "adv_create_in0":
        user_temp_set(user_id, "ad_title", message.text)
        await message.answer("Введите текст объявления", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in1")
        return
    if user_state == "adv_create_in1":
        user_temp_set(user_id, "ad_text", message.text)
        await message.answer("Введите максимальное кол-во показов", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in2")
        return
    if user_state == "adv_create_in2":
        user_temp_set(user_id, "impressions_limit", message.text)
        await message.answer("Введите максимальное кол-во переходов", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in3")
        return
    if user_state == "adv_create_in3":
        user_temp_set(user_id, "clicks_limit", message.text)
        await message.answer("Введите цену за показ", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in4")
        return
    if user_state == "adv_create_in4":
        user_temp_set(user_id, "cost_per_impression", message.text)
        await message.answer("Введите цену за переход", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in5")
        return
    if user_state == "adv_create_in5":
        user_temp_set(user_id, "cost_per_click", message.text)
        await message.answer("Введите начало показа", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in6")
        return
    if user_state == "adv_create_in6":
        user_temp_set(user_id, "start_date", message.text)
        await message.answer("Введите конец показа", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in7")
        return
    if user_state == "adv_create_in7":
        user_temp_set(user_id, "end_date", message.text)
        await message.answer("Введите полы (MALE, FEMALE, ALL), для которых будет показываться объявление (\"-\", если любой)", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in8")
        return
    if user_state == "adv_create_in8":
        if message.text != "-": user_temp_set(user_id, "gender", message.text)
        await message.answer("Введите минимальный возраст (\"-\", если любой)", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in9")
        return
    if user_state == "adv_create_in9":
        if message.text != "-": user_temp_set(user_id, "age_from", message.text)
        await message.answer("Введите максимальный возраст (\"-\", если любой)", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in10")
        return
    if user_state == "adv_create_in10":
        if message.text != "-": user_temp_set(user_id, "age_to", message.text)
        await message.answer("Введите локации, для которых будет показываться объявление (\"-\", если любая)", reply_markup=cancel_kb)
        set_state_for_user(user_id, "adv_create_in11")
        return
    if user_state == "adv_create_in11":
        if message.text != "-": user_temp_set(user_id, "location", message.text)
        try:
            json = {
                "impressions_limit": int(user_temp_get(user_id, "impressions_limit")),
                "clicks_limit": int(user_temp_get(user_id, "clicks_limit")),
                "cost_per_impression": float(user_temp_get(user_id, "cost_per_impression")),
                "cost_per_click": float(user_temp_get(user_id, "cost_per_click")),
                "ad_title": user_temp_get(user_id, "ad_title"),
                "ad_text": user_temp_get(user_id, "ad_text"),
                "start_date": int(user_temp_get(user_id, "start_date")),
                "end_date": int(user_temp_get(user_id, "end_date")),
                "targeting": {}
            }
            if user_temp_get(user_id, "gender") != None: json["targeting"]["gender"] = user_temp_get(user_id, "end_date")
            if user_temp_get(user_id, "age_from") != None: json["targeting"]["age_from"] = int(user_temp_get(user_id, "age_from"))
            if user_temp_get(user_id, "age_to") != None: json["targeting"]["age_to"] = int(user_temp_get(user_id, "age_to"))
            if user_temp_get(user_id, "location") != None: json["targeting"]["location"] = user_temp_get(user_id, "location")
        except Exception as e:
            await message.answer("Что-то пошло не так...", reply_markup=cancel_kb)
            raise e
        try:
            r = await client.post(f"http://{MAINAPI_HOST}/advertisers/{get_adv_id(user_id)}/campaigns", json=json)
            if r.status_code == 400:
                await message.answer(f"Что-то не так с введёнными данными, попробуйте ещё раз.", reply_markup=default_kb)
            elif r.status_code == 201:
                await message.answer(f"Объявление {r.json()['campaign_id']} создано!", reply_markup=default_kb)
            else:
                raise Exception(f"Not valid code! {r.status_code}")
        except Exception as e:
            await message.answer("Что-то пошло не так...", reply_markup=default_kb)
            raise e
        set_state_for_user(user_id, None)
        user_delete_all_temp(user_id)
    
    # Просмотреть объявления
    if message.text == "Просмотреть объявления" and user_state == None:
        r = await client.get(f"http://{MAINAPI_HOST}/advertisers/{get_adv_id(user_id)}/campaigns")
        r_json = r.json()
        
        mod_status_to_text = {
            "pending": "ожидает модерацию... ⏳",
            "succesful": "прошло модерацию ✅",
            "failed": "не прошло модерацию ❌"
        }

        for i in r_json:
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Удалить", callback_data=f"ad_delete_{i['campaign_id']}"),
                    types.InlineKeyboardButton(text="Изменить", callback_data=f"ad_edit_{i['campaign_id']}"),
                ],
                [types.InlineKeyboardButton(text="Просмотреть статистику", callback_data=f"ad_stats_{i['campaign_id']}")],
                [types.InlineKeyboardButton(text="Просмотреть все данные", callback_data=f"ad_alldata_{i['campaign_id']}")]
            ])
            msg = f"Объявление {i['campaign_id']}\n\"{i['ad_title']}\""
            try:
                msg += f"\nСтатус: {mod_status_to_text[i['moderation_status']]}"
            except Exception as e:
                pass
            await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=kb)
        return
    
    # Просмотреть статистику по всем объявлениям
    if message.text == "Просмотреть статистику по всем объявлениям" and user_state == None:
        r = await client.get(f"http://{MAINAPI_HOST}/stats/advertisers/{get_adv_id(user_id)}/campaigns")
        r_json = r.json()
        msg = f"Статистика по всем объявлениям:\n\
Просмотры: {r_json['impressions_count']}\n\
Переходы: {r_json['clicks_count']}\n\
Конверсия: {round(r_json['conversion'], 2)}%\n\
Затрачено на показы: {round(r_json['spent_impressions'], 2)}\n\
Затрачено на переходы: {round(r_json['spent_clicks'], 2)}\n\
Затрачено всего: {round(r_json['spent_total'], 2)}"
        await message.answer(msg, parse_mode=ParseMode.HTML)
        return
    
    # Редактировать объявление
    if user_state == "adedit":
        ad_id = user_temp_get(user_id, "ad_id")
        adv_id = get_adv_id(user_id)
        field = user_temp_get(user_id, "field")

        client = http3.AsyncClient()

        try:
            r = await client.get(f"http://{MAINAPI_HOST}/advertisers/{adv_id}/campaigns/{ad_id}")
            campaign = r.json()
            del campaign["campaign_id"]
            del campaign["advertiser_id"]
            try:
                del campaign["moderation_status"]
            except Exception as e:
                pass
            if not "targeting" in campaign.keys(): campaign["targeting"] = {}

            if field == "imprlimit":
                campaign["impressions_limit"] = int(message.text)
            if field == "clklimit":
                campaign["clicks_limit"] = int(message.text)
            if field == "imprcost":
                campaign["cost_per_impression"] = float(message.text)
            if field == "clkcost":
                campaign["cost_per_click"] = float(message.text)
            if field == "title":
                campaign["ad_title"] = message.text
            if field == "text":
                campaign["ad_text"] = message.text
            if field == "startdate":
                campaign["start_date"] = int(message.text)
            if field == "enddate":
                campaign["end_date"] = int(message.text)
            if field == "gender":
                if message.text == "-":
                    campaign["targeting"]["gender"] = None
                else:
                    campaign["targeting"]["gender"] = message.text
            if field == "location":
                if message.text == "-":
                    campaign["targeting"]["location"] = None
                else:
                    campaign["targeting"]["location"] = message.text
            if field == "agefrom":
                if message.text == "-":
                    campaign["targeting"]["age_from"] = None
                else:
                    campaign["targeting"]["age_from"] = int(message.text)
            if field == "ageto":
                if message.text == "-":
                    campaign["targeting"]["age_to"] = None
                else:
                    campaign["targeting"]["age_to"] = int(message.text)

            r = await client.put(f"http://{MAINAPI_HOST}/advertisers/{adv_id}/campaigns/{ad_id}", json=campaign)
            if r.status_code == 200:
                await message.answer("Изменения сохранены.", reply_markup=default_kb)
            elif r.status_code == 400:
                await message.answer(f"Что-то не так с введёнными данными, попробуйте ещё раз.", reply_markup=default_kb)
            else:
                raise Exception(f"Not valid code! {r.status_code}")
        except Exception as e:
            print(e)
            await message.answer("Что-то пошло не так...", reply_markup=default_kb)

        set_state_for_user(user_id, None)
        user_delete_all_temp(user_id)

        return

    # Выйти из профиля
    if message.text == "Выйти из профиля" and user_state == None:
        db = DB()
        db.redis_con.delete(f"tgbot_auth_{message.from_user.id}")
        set_state_for_user(message.from_user.id, None)
        user_delete_all_temp(message.from_user.id)
        db.end()
        await message.answer(f"Здравствуйте, пожалуйста, введите свой UUID.", reply_markup=no_kb)
        return

    if user_state == None:
        await message.answer("Извините, я вас не понял 🥺", reply_markup=default_kb)

@dp.callback_query(F.data.startswith("addelete_"))
async def callbacks_ad(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    adv_id = get_adv_id(user_id)

    arr = callback.data.split("_")
    action = arr[1]
    ad_id = arr[2]

    client = http3.AsyncClient()

    if action == "yes":
        r = await client.delete(f"http://{MAINAPI_HOST}/advertisers/{adv_id}/campaigns/{ad_id}")
        if r.status_code == 204:
            await callback.message.answer(text=f"Объявление {ad_id} удалено!", parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(text=f"Что-то пошло не так!", parse_mode=ParseMode.HTML)
            raise Exception(f"Status code not 204! {r.status_code}")
    else:
        pass
    await callback.message.delete()
    
    await callback.answer()

@dp.callback_query(F.data.startswith("adedit_"))
async def callbacks_adedit(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    adv_id = get_adv_id(user_id)

    arr = callback.data.split("_")
    action = arr[1]
    ad_id = arr[2]

    if action == "cancel":
        await callback.message.delete()
    else:
        set_state_for_user(user_id, "adedit")
        user_temp_set(user_id, "field", action)
        user_temp_set(user_id, "ad_id", ad_id)
        await callback.message.answer("Введите новое значение", reply_markup=cancel_kb)

    await callback.answer()

def get_val_or_none(d:dict, k):
    if k in d.keys():
        return d[k]
    return None

@dp.callback_query(F.data.startswith("ad_"))
async def callbacks_ad(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    adv_id = get_adv_id(user_id)

    arr = callback.data.split("_")
    action = arr[1]
    ad_id = arr[2]

    client = http3.AsyncClient()

    if action == "stats":
        r = await client.get(f"http://{MAINAPI_HOST}/stats/campaigns/{ad_id}")
        r_json = r.json()
        msg = f"Статистика по объявлению \"{ad_id}\"\n\
Просмотры: {r_json['impressions_count']}\n\
Переходы: {r_json['clicks_count']}\n\
Конверсия: {round(r_json['conversion'], 2)}%\n\
Затрачено на показы: {round(r_json['spent_impressions'], 2)}\n\
Затрачено на переходы: {round(r_json['spent_clicks'], 2)}\n\
Затрачено всего: {round(r_json['spent_total'], 2)}"
        await callback.message.answer(text=msg, parse_mode=ParseMode.HTML, reply_markup=default_kb)
    if action == "delete":
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Да", callback_data=f"addelete_yes_{ad_id}"),
                    types.InlineKeyboardButton(text="Нет", callback_data=f"addelete_no_{ad_id}"),
                ],
            ])
        await callback.message.answer(text=f"Вы уверены, что хотите удалить объявление {ad_id}", parse_mode=ParseMode.HTML, reply_markup=kb)
    if action == "edit":
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Лимит показов", callback_data=f"adedit_imprlimit_{ad_id}"),
                types.InlineKeyboardButton(text="Лимит переходов", callback_data=f"adedit_clklimit_{ad_id}"),
            ],
            [
                types.InlineKeyboardButton(text="Цену за показ", callback_data=f"adedit_imprcost_{ad_id}"),
                types.InlineKeyboardButton(text="Цену за переход", callback_data=f"adedit_clkcost_{ad_id}"),
            ],
            [
                types.InlineKeyboardButton(text="Заголовок", callback_data=f"adedit_title_{ad_id}"),
                types.InlineKeyboardButton(text="Текст", callback_data=f"adedit_text_{ad_id}"),
            ],
            [
                types.InlineKeyboardButton(text="Дата начала", callback_data=f"adedit_startdate_{ad_id}"),
                types.InlineKeyboardButton(text="Дата конца", callback_data=f"adedit_enddate_{ad_id}"),
            ],
            [
                types.InlineKeyboardButton(text="Полы", callback_data=f"adedit_gender_{ad_id}"),
                types.InlineKeyboardButton(text="Локацию", callback_data=f"adedit_location_{ad_id}"),
            ],
            [
                types.InlineKeyboardButton(text="Возраст от", callback_data=f"adedit_agefrom_{ad_id}"),
                types.InlineKeyboardButton(text="Возраст до", callback_data=f"adedit_ageto_{ad_id}"),
            ],
            [
                types.InlineKeyboardButton(text="Отмена", callback_data=f"adedit_cancel_{ad_id}")
            ]
        ])
        await callback.message.answer(text=f"Что вы хотите редактировать?", parse_mode=ParseMode.HTML, reply_markup=kb)

    if action == "alldata":
        r = await client.get(f"http://{MAINAPI_HOST}/advertisers/{adv_id}/campaigns/{ad_id}")
        campaign = r.json()
        msg1 = f"Объявление {campaign['campaign_id']}:\n\
Лимит показов: {campaign['impressions_limit']}\n\
Лимит переходов: {campaign['clicks_limit']}\n\
Цена за показ: {campaign['cost_per_impression']}\n\
Цена за переход: {campaign['cost_per_click']}\n\
Заголовок: {campaign['ad_title']}\n\
Текст: {campaign['ad_text']}\n\
Дата начала: {campaign['start_date']}\n\
Дата конца: {campaign['end_date']}"
        msg2 = f"Таргетинг для объявления {campaign['campaign_id']}:"
        if get_val_or_none(campaign, "targeting") != None:
            if get_val_or_none(campaign["targeting"], "gender") != None:
                msg2 += f"\nПол: {campaign['targeting']['gender']}"
            if get_val_or_none(campaign["targeting"], "age_from") != None:
                msg2 += f"\nВозраст от: {campaign['targeting']['age_from']}"
            if get_val_or_none(campaign["targeting"], "age_to") != None:
                msg2 += f"\nВозраст до: {campaign['targeting']['age_to']}"
            if get_val_or_none(campaign["targeting"], "location") != None:
                msg2 += f"\nЛокация: {campaign['targeting']['location']}"
        await callback.message.answer(msg1, parse_mode=ParseMode.HTML)
        await callback.message.answer(msg2, parse_mode=ParseMode.HTML, reply_markup=default_kb)

    await callback.answer()

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())