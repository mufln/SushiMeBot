import os
import platform
#Bot token
if platform.system() in ("Windows","Darwin"):
    TOKEN = "1634628039:AAGbIRu7yNWoIPfSbT8cqc9bq9ebxNc0oRs"
    DB_USER = "tg_bot"
    DB_PASSWORD = "Aa@12345678"
else:
    TOKEN = os.environ.get("TOKEN")
    # webhook path '/webhook/'
    WEBHOOK_PATH = "/sushime_bot/"
    # aiohttp app ip:port
    HOST_IP = "127.0.0.1"
    HOST_PORT = 8080
    # webhook base url 'https://<ip or domain>:port'
    WEBHOOK_BASE_URL = os.environ.get("BASE_URL")
    WEBHOOK_SECRET = 'aoaommm'
    # SSL cert pathes
    SSL_CERT = '/ssl_cert/cert.pem'
    SSL_KEY = '/ssl_cert/private.key'
    # db variables
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

DB_HOST = "localhost"
DB_NAME = "SushiMe"
