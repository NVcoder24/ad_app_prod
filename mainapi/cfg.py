import os

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "prod_mainapi")
REDIS_HOST = os.getenv("REDIS_HOST", 'localhost')
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

IMAGES_MAXSIZE = int(os.getenv("IMAGES_MAXSIZE", "5000000"))
IMAGES_FILETYPES = os.getenv("IMAGES_FILETYPES", "png,jpg,jpeg,tiff,gif,webp,bmp").split(",")

MAINAPI_HOST = os.getenv("MAINAPI_HOST", "127.0.0.1:8080")
MODERATION_HOST = os.getenv("MODERATION_HOST", "127.0.0.1:8001")
GRAFANA_API_HOST = os.getenv("GRAFANA_API_HOST", "127.0.0.1:8002")
LLM_API_HOST = os.getenv("LLM_API_HOST", "127.0.0.1:8003")