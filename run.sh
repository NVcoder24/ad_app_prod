#!/bin/bash

cd /grafanaapi
exec fastapi run main.py --port=8002 --host=0.0.0.0 > /grafanaapi_log.txt &

cd /llmapi
exec fastapi run main.py --port=8003 --host=0.0.0.0 > /llmapi_log.txt &

cd /mainapi
exec fastapi run main.py --port=8080 --host=0.0.0.0 > /mainapi_log.txt &

cd /moderationapi
exec fastapi run server.py --port=8001 --host=0.0.0.0 > /moderationapi_server_log.txt &
exec python queue.py > /moderationapi_queue_log.txt &

cd /tgbot
exec python main.py > /tgbot_log.txt