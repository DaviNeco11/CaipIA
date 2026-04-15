import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
URL_API = os.getenv("URL_API", "http://localhost:8000")