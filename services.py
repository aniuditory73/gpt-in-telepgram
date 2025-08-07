from openai import OpenAI
from config import OPENROUTER_API_KEY

# Инициализация клиента OpenRouter (OpenAI-совместимый)
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)
