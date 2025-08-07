import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
    raise RuntimeError("TELEGRAM_TOKEN и OPENAI_API_KEY должны быть установлены в .env")
