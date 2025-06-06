import os

TGBOT_REDIS_HOST = os.getenv("TGBOT_REDIS_HOST", 'localhost')
TGBOT_REDIS_PORT = os.getenv("TGBOT_REDIS_PORT", 6379)
TGBOT_REDIS_DB = int(os.getenv("TGBOT_REDIS_DB", "1"))

MAINAPI_HOST = os.getenv("MAINAPI_HOST", "127.0.0.1:8080")
MODERATION_HOST = os.getenv("MODERATION_HOST", "127.0.0.1:8001")
GRAFANA_API_HOST = os.getenv("GRAFANA_API_HOST", "127.0.0.1:8002")
LLM_API_HOST = os.getenv("LLM_API_HOST", "127.0.0.1:8003")

TGBOT_TOKEN = os.getenv("TGBOT_TOKEN")