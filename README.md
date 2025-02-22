# Документация
## Главное API
### ✔️ Описание
Это API с обязательными пунктами задания.

### ❔ Обоснование
Я решил использовать Python + FastAPI для этого API, т.к. я уже хорошо знаком с этими 
технологиями и был уверен, что с их помощью смогу решить задачу.

Эндпоинты я разбил по документации FastAPI в папке routes с использованием `fastapi.APIRouter`.
В визуализации файла openapi в свагере, эндпоинты были разбиты по категориям, так же я решил 
разбить их по файлам в структуре моего проекта.

Для валидации данных я использую Pydantic, т.к. уже с ним знаком, он является "стандартом" для валидации
данных с FastAPI.

Почему SQL база данных? Данные в проекте имеют фиксированную структуру, SQL предоставляет
возможность писать большие запросы с разными условиями, join'ами, т.д., что помогает
перенести нагрузку с python и в общем ускорить работу API (особо хорошо это видно
на примере алгоритма показа - вся работа по нахождению объявлений перенесена
на БД).

Почему не ORM? ORM многие, включая меня, считают анти-паттерном. ORM замедляет работу
приложения, отсутствует гибкость в работе с БД (а мне она очень даже нужна). Мне проще 
и быстрее написать запрос на голом SQL.

В качестве основной БД я выбрал PostgreSQL, т.к. в отличии от других БД,
которые я знаю, например MySQL, он лучше справляется с ReadWrite-heavy задачами (что важно,
т.к. моё решение постоянно обновляет статистику и другие параметры),
где MySQL лучше справляется с Read-heavy задачами.

Так же я выбрал Redis для кэширования. По подсказке организаторов,
я в нём храню текущую дату.

### ❗️❗️❗️ Важности
В эндпоинте `PUT /advertisers/{advertiserId}/campaigns/{campaignId}`, по архитектуре
REST API, PUT перезаписывает данные. В моём решении валидация данных в этом эндпоинте
производится так же, как и в `POST /advertisers/{advertiserId}/campaigns` - всё, кроме
`targeting` обязательно. Если параметра из targeting нет, он считается, как null.

Про коды HTTP. Тут я тоже старался максимально придерживаться стандартам
архитектуры REST API. Там, где ведётся проверка на существование условного UUID
из URL, при ошибке возвращается не ошибка валидации (400), а не найдено (404).

В ответах эндпоинтов, возращающих объявления, при включенной модерации текстов,
добавляется параметр `moderation_status`, у него всего 3 значения -
`succesful`, `pending`, `failed`, соответственно модерация пройдена, ждёт
модерации, модерация не пройдена.

В эндпоинтах по типу `...{advertiserId}/campaigns/{campaignId}...` ведётся сначала
проверка на существование advertiserId, а потом проверка на существование
campaignId с данным advertiserId. Если не найдено объявление campaignId с данным 
advertiserId, то возвращается не 403 или 400, а 404 (объявление не найдено).

## Добавление изображений в рекламных объявлениях
### ✔️ Описание
Функционал этого задания имплементирован в коде главного API.
В ответах эндпоинтов, возращающих объявления, при наличии изображения,
добавляется параметр `image`. Чтобы получить URL изображения, нужно
перед значением этого параметра подставить /images/. Пример:
`http://127.0.0.1:8080/images/2beae2dd-de9d-422f-82e4-43c8216c8412.png`.

Добавлены эндпоинты:
### PUT `/advertisers/{advertiserId}/campaigns/{campaignId}/image`
Эндпоинт для добавления/изменения изображения.

Файл изображения берёт из form-data.

Пример использования из postman:

![alt text](https://github.com/NVcoder24/ad_app_prod/blob/main/readme_resources/Screenshot_4389.png)

Принимает следующие типы изображений: png,jpg,jpeg,tiff,gif,webp,bmp (меняются через переменную среды `IMAGES_FILETYPES`)

Так же имеется ограничение по размеру в байтах (изменяется через переменную среды `IMAGES_MAXSIZE`, дефолт: 5.000.000)

### DELETE `/advertisers/{advertiserId}/campaigns/{campaignId}/image`
Эндпоинт для удаления изображения.

### GET `/images/{image}`
Эндпоинт для получения изображения. `{image}` - параметр из ответа эндпоинтов, 
которые возвращают объявления.

## Визуализация данных
### ✔️ Описание
Для визуализации данных было реализовано API для Grafana (используется
датасорс `simpod-json-datasource`). Готовый JSON дашборда:
`solution/Статистика рекламодателя-1740145250823.json`:

![alt text](https://github.com/NVcoder24/ad_app_prod/blob/main/readme_resources/Screenshot_4396.png)

### ❗️❗️❗️ Важности
Если вы используете графану из `Dockerfile`, то она работает на 3001 порте,
в параметрах датасорса нужно указать URL `web:8002`:

![alt text](https://github.com/NVcoder24/ad_app_prod/blob/main/readme_resources/Screenshot_4397.png)

## Интеграция с TG ботом
### ✔️ Описание
Реализована простая авторизация (связывание телеграма с id рекламодателя),
создание объявлений, изменение объявлений, просмотр всех объявлений, просмотр
всех данных объявления, просмотр статистики объявления, просмтор статистики 
по всем объявлениям.

Бот хранит все данные в redis, потому что быстро, да и хранить боту особо нечего.
Хранит он следующее: связки id телеграма - id рекламодателя, состояния пользователей
(например, что пользователь создаёт объявление, какое он сейчас поле вводит),
временные данные (условные значения полей при создании объявлений)

### ❗️❗️❗️ Важности
API ключ TG bot API хранится в переменной среды, как `TGBOT_TOKEN`. Бот: @prod2tgbot_bot

## Модерация текстов рекламных кампаний
### ✔️ Описание
Для модерации текстов был создан отдельный API. Он работает на порте 8001.
У этого сервиса есть 2 программы: http сервер, который принимает запросы, а так же
обработчик очереди.

Когда создаётся или изменяется объявление, главное API шлёт запрос на модерацию в
API модерации, который содержит id, заголовок и текст объявления. API модерации 
сохраняет эти данные в своей БД.

Дальше обработчик очереди сгружает из БД заявку на модерацию, модерирует тексты,
отправляет на эндпоинт главного API результат модерации и дополнительное сообщение,
если объявление не прошло модерацию.

Модерация производится по банвордам, которые хранятся в той же базе данных. Для
просмотра и редактирования списков банвордов, у API модерации есть свои эндпоинты:

### `POST /swear_words`
Загрузка банвордов пачкой.
Пример тела запроса:
```json
[
    "плохое слово 1",
    "плохое слово 2"
]
```

### `DELETE /swear_words`
Загрузка банвордов пачкой.
Пример тела запроса:
```json
[
    "плохое слово 1",
    "плохое слово 2"
]
```

### `GET /swear_words`
Возвращает все банворды (без пагинации)
Пример ответа:
```json
[
    "плохое слово 1",
    "плохое слово 2",
    "плохое слово 3"
]
```

Эндпоинт API модерации для планирования модерации объявления:
### `POST /schedule`
Пример тела запроса:
```json
{
    "ad_id": "6099643c-734d-4a2a-82c8-ca502cb687e2",
    "ad_title": "Я хочу испортить репутацию этому сервису!",
    "ad_text": "Вы плохое слово 1! плохое слово 2! Чтоб вы плохое слово 3 плохое слово 4!"
}
```

### ❗️❗️❗️ Важности
Для модерации были созданы эндпоинты для главного API:
### `POST /moderation/use_moderation/{state}`
`state` принимает 2 значения: `true` - включить модерацию, `false` - выключить модерацию.

Все слова загружаются в нижнем регистре.

Для быстрой загрузки из txt файла есть скрипт `solution/moderationapi/load_swear_words.py`.
Он напрямую в БД загружает слова из файла `swear_words.txt` из текущей директории. Слова
в нижнем регистре, по 1 слову на строку. Пример:

`swear_words.txt`
```
плохое слово 1
плохое слово 2
...
плохое слово N
```

### `POST /moderation/results`
На этот эндпоинт обработчик очереди присылает результаты модерации.
Пример тела запроса:
```json
{
    "ad_id": "6099643c-734d-4a2a-82c8-ca502cb687e2",
    "is_good": false,
    "message": "ругательные слова"
}
```

## Генерация текстов с LLM
### ✔️ Описание
Присутствует генерация текста объявления по его заголовку с помощью YaGPT (модель yandexgpt-lite/rc).

Для этого имплементировано отдельное API. У этого API всего 1 эндпоинт:
### `GET /generate_text`
Пример тела запроса:
```json
{
    "ad_title": "Магазин оружия \"У ВАСИЛИЧА\""
}
```
Пример ответа:
```json
{
    "ad_text": "Магазин оружия «У ВАСИЛИЧА» — ваш надёжный поставщик качественных товаров. В нашем ассортименте — широкий выбор ружей, пистолетов и аксессуаров. Приходите за покупками!"
}
```

### ❗️❗️❗️ Важности
Каталог и API ключ YaGPT хранится в переменных среды, как `YAGPT_CATALOG` и `YAGPT_KEY` соответственно.

# Инструкция по запуску приложения
Для запуска нужно перейти в каталог solution и исполнить `docker compose up`.

Если нужно пустить приложение не под docker, то нужно:
1. установить все переменные среды, как в файле `Dockerfile`
2. Установить все библиотеки из requirements.txt
3. Запустить на указанном в ENV хосте и порте postgres, redis
4. Запустить через `fastapi run [имя скрипта] --port=[порт] --host=[хост]` на указанных в ENV портах все python сервера
    1. `solution/mainapi` - `main.py`
    2. `solution/llmapi` - `main.py`
    3. `solution/grafanaapi` - `main.py`
    4. `solution/moderationapi` - `server.py`
5. Запустить через `python queue.py` ообработчик очереди в `solution/moderationapi`
6. Запустить через `python main.py` тг бот в `solution/tgbot`
7. Готово, приложение должно работать.

### ❗️❗️❗️ Важности
В `Dockerfile` уже прописаны `YAGPT_CATALOG`, `YAGPT_KEY`, `TGBOT_TOKEN`.
Пожалуйста, не обанкротьте меня, я вам верю 🥺

# Демонстрация работы приложения
Работа ТГ бота: https://rutube.ru/video/private/4dbc9025dd1d579bef15c7754239fb36/?p=1LZ205bYbhle-HkCVVU8Sw

Работа модерации: https://rutube.ru/video/private/b940ad38f7d69e6a215cccf62a282af8/?p=S8rVZ1WLIhOsYyoKC-6QEQ

Картинки объявлений: https://rutube.ru/video/private/9e828a3f35b042daa9624a8fdf5e7d36/?p=M8SyvxGK38SBYoqrG9-rpA

Unit тесты: https://rutube.ru/video/private/64041de7c4327c3c3725f3675971d3a1/?p=oVY9Gnl6C2Znc0FOmDt-TQ

Grafana: https://rutube.ru/video/private/518b4a45e7599221e91729aff287d86c/?p=8DFGjIU55DG_il9udCQ_Sg

E2E тесты: https://rutube.ru/video/private/a4582abe0a72737e79052744af8aae37/?p=bgRUxH70nR5Eaxy1e-jbeg

Docker compose up: https://rutube.ru/video/private/c376af212866ff25550abbc0d9d8ec9b/?p=GwwYl6JHwve2HW5u_e31ZQ

# Схема данных СУБД
### БД - Главное API
![alt text](https://github.com/NVcoder24/ad_app_prod/blob/main/readme_resources/prod2_1.png)
### БД - API модерации
![alt text](https://github.com/NVcoder24/ad_app_prod/blob/main/readme_resources/prod2_mod_1.png)
№ | Название сервиса | Часть сервиса | Файл | Внешний адрес (при запуске из `Dockerfile`)
--- | --- | --- | --- | ---
1 | Main API | FastAPI app |  `solution/mainapi/main.py` | `localhost:8080`
2 | Moderation API | FastAPI app | `solution/moderationapi/server.py` | `localhost:8001`
3 | Moderation API | Moderation queue | `solution/moderationapi/queue.py` | -
4 | Grafana API | FastAPI app | `solution/grafanaapi/main.py` | `localhost:8002`
5 | LLM API | FastAPI app | `solution/llmapi/main.py` | `localhost:8003`
6 | Telegram bot | AIOGram app | `solution/tgbot/main.py` | -
7 | Grafana | - | - | `localhost:3001`
8 | PostgreSQL | - | - | `localhost:5433`
9 | Redis | - | - | `localhost:6380`

# Описание работы основных точек входа
### Диаграма - архитектура приложения
![alt text](https://github.com/NVcoder24/ad_app_prod/blob/main/readme_resources/architecture.png)

### Описание работы алгоритма
Весь алгоритм - один большой запрос SQL.
Разберу его по блокам.

Выберем из кампаний все столбцы
```sql
SELECT campaigns.* FROM campaigns 
```

Добавим join'ом ML скоры для пары рекламодатель - клиент
```sql
LEFT JOIN mlscores on (mlscores.advertiser_id = campaigns.advertiser_id AND mlscores.client_id = %s) 
```

Для проверки лимитов в дальнейшем, join'ом добавим клики и показы для этого объявления у текущего клиента
```sql
LEFT JOIN clicks on (clicks.campaign_id = campaigns.id AND clicks.client_id = %s)
LEFT JOIN impressions on (impressions.campaign_id = campaigns.id AND impressions.client_id = %s)
```

Дальше начинаем блок с условиями
```sql
WHERE (
```

Проверим, всё ли хорошо с лимитами, посчитав кол-во строк из ранее заjoin'еных строк показов,
не забываем проверить, попали ли мы по периоду активности рекламы.
```sql
(SELECT COUNT(*) FROM impressions WHERE campaign_id = campaigns.id AND impressions.affects_stats = true) < impressions_limit AND
%s >= start_date AND %s <= end_date AND 
```

Проверим, всё ли хорошо по таргетингу
```sql
(gender is NULL or gender LIKE %s or gender LIKE 'ALL') AND (age_from IS NULL or age_from <= %s) AND (age_to IS NULL or age_to >= %s) AND 
(location IS NULL or location LIKE %s) AND
```

Т.к. у меня есть модерация текстов, добавим проверку, прошло ли
объявление модерацию
```sql
is_moderated = true
```

Конец блока условий
```sql
) 
```

Сгруппируем по id объявлений и ML скорам
```sql
GROUP BY (campaigns.id, mlscores.score)
```

Начнём блок сортировки
```sql
ORDER BY
```

Отсортируем по кликам (по возрастанию), по показам (по возрастанию), по ML скорам (по убыванию).
Не забываем, что ML скора может не быть в БД, поэтому используем `COALESCE`, чтобы в случае
чего, считать скор за 0.
```sql
COUNT(clicks.*) ASC,
COUNT(impressions.*) ASC,
COALESCE(mlscores.score, 0) DESC 
```

"Нам нужно выдать только 1 рекламу, не будем мучать БД"
```sql
LIMIT 1
```

Итого получается вот такой запрос (из файла `solution/mainapi/routes/ads.py:30`):
```sql
-- Селектим всё только от таблицы с рекламами
SELECT campaigns.* FROM campaigns 

-- Добавляем строке ML скор пары рекламодатель - клиент
LEFT JOIN mlscores on (mlscores.advertiser_id = campaigns.advertiser_id AND mlscores.client_id = %s) 

-- Добавляем строке показы этой рекламы пользователю
LEFT JOIN clicks on (clicks.campaign_id = campaigns.id AND clicks.client_id = %s)

-- Добавляем строке показы этой рекламы пользователю
LEFT JOIN impressions on (impressions.campaign_id = campaigns.id AND impressions.client_id = %s)

-- Условия для рекламы
WHERE (
-- Условия активности рекламы
(SELECT COUNT(*) FROM impressions WHERE campaign_id = campaigns.id AND impressions.affects_stats = true) < impressions_limit AND
%s >= start_date AND %s <= end_date AND 

-- Условия по таргету
(gender is NULL or gender LIKE %s or gender LIKE 'ALL') AND (age_from IS NULL or age_from <= %s) AND (age_to IS NULL or age_to >= %s) AND 
(location IS NULL or location LIKE %s) AND

-- Условия по модерации
is_moderated = true
) 

-- Группировка по id рекламы
GROUP BY (campaigns.id, mlscores.score)

-- Сортировка
ORDER BY
-- Сортируем по кликам пользователя
COUNT(clicks.*) ASC,
-- Сортируем по показам пользователю
COUNT(impressions.*) ASC,
-- Сортируем по скору, если скора нет - считаем его за 0 
COALESCE(mlscores.score, 0) DESC 

-- Нам нужно выдать только 1 рекламу, не будем мучать БД
LIMIT 1
```

Почему нет проверки на релевантность? Сначала я делал проверку, чтобы
`([скор для пары клиент - рекламодатель] - MIN(mlscores.score)) / (MAX(mlscores.score) - MIN(mlscores.score))`
был больше 0.7 (относительная релевантность 70%), но это сильно увеличивало
процент 404 ошибок в выдаче => сильно снижало прибыль. Тестировал я это через
мой e2e тест (`solution/tests/mainapi/e2e/test.ipynb`), который получился по
функционалу почти 1 в 1, как CI тестирование от организаторов.
