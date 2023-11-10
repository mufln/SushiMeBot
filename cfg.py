import os
import platform
#Bot token
if platform.system() in ("Windows","Darwin"): TOKEN = os.environ.get("TEST_BOT_TOKEN")
else: TOKEN = os.environ.get("TOKEN")
#webhook path '/webhook'
WEBHOOK_PATH = "/sushime_bot"
#aiohttp app ip:port
HOST_IP = "127.0.0.1"
HOST_PORT = 8080
#webhook base url 'https://<ip or domain>:port'
WEBHOOK_BASE_URL = ""
WEBHOOK_SECRET = 'aoaommm'
#SSL cert pathes
SSL_CERT = '../ssl_cert/cert.pem'
SSL_KEY = '../ssl_cert/private.key'
#db variables
DB_HOST = "localhost"
if platform.system() in ("Windows","Darwin"):
    DB_USER = os.environ.get("TEST_USER")
    DB_PASSWORD = os.environ.get("TEST_PASSWORD")
else:
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = "SushiMe"
