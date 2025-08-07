from aiogram import types, Dispatcher
from aiogram.filters.command import Command
from aiogram.methods import SendChatAction
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from services import client
from utils import clean_html


MODELS = {
    "horizon_beta": "openrouter/horizon-beta",
    "deepseek_v3": "deepseek/deepseek-chat-v3-0324:free",
    "mistral_7b": "mistralai/mistral-7b-instruct:free"
}

ROLES = {
    "programmer": "👨‍💻 Программист",
    "writer": "✍️ Писатель",
    "teacher": "🎓 Учитель",
    "analyst": "🕵️ Аналитик"
}

user_models = {}
user_roles = {}


def get_models_keyboard() -> InlineKeyboardMarkup:
    buttons_data = [
        ("🌅 Horizon Beta", "horizon_beta"),
        ("🔎 Deepseek V3", "deepseek_v3"),
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"set_model:{key}")]
        for name, key in buttons_data
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_roles_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"set_role:{key}")]
        for key, name in ROLES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def cmd_start(message: types.Message):
    await message.answer(
        "🤖 <b>Привет!</b> Я - бот с нейросетями.\n"
        "Выбери модель командой /models, роль — /roles или просто задай вопрос.\n"
        "<i>Чем помочь?</i>",
        parse_mode="HTML"
    )


async def cmd_models(message: types.Message):
    await message.answer(
        "Выбери модель для общения:",
        reply_markup=get_models_keyboard()
    )


async def set_model_callback(call: CallbackQuery):
    user_id = call.from_user.id
    model_key = call.data.split(":", 1)[1]

    if model_key in MODELS:
        user_models[user_id] = MODELS[model_key]
        await call.answer(f"Модель установлена: {MODELS[model_key]}", show_alert=True)
        await call.message.edit_text(f"Вы выбрали модель:\n<b>{MODELS[model_key]}</b>", parse_mode="HTML")
    else:
        await call.answer("Ошибка: модель не найдена", show_alert=True)


async def cmd_roles(message: types.Message):
    await message.answer(
        "Выбери роль для нейросети:",
        reply_markup=get_roles_keyboard()
    )


async def set_role_callback(call: CallbackQuery):
    user_id = call.from_user.id
    role_key = call.data.split(":", 1)[1]

    if role_key in ROLES:
        user_roles[user_id] = role_key
        await call.answer(f"Роль установлена: {ROLES[role_key]}", show_alert=True)
        await call.message.edit_text(f"Вы выбрали роль:\n<b>{ROLES[role_key]}</b>", parse_mode="HTML")
    else:
        await call.answer("Ошибка: роль не найдена", show_alert=True)


def get_system_prompt(role_key: str) -> str:
    if role_key == "programmer":
        return ("Ты — опытный программист, который пишет чистый, понятный код и ясно объясняет технические вопросы. "
                "Отвечай по существу, с примерами, если нужно.""Форматируй текст с помощью HTML. "
                "Не используй Markdown. Немного разбавь текст эмодзи, но не перебарщивай.""Не используй двойной enter ля разделения строк, текст должен быть читаемым")
    elif role_key == "writer":
        return ("Ты — творческий писатель, который помогает создавать яркие, живые тексты и идеи. "
                "Пиши интересно и вдохновляюще.""Отвечай кратко, максимум 20 предложений, без лишнего текста. Форматируй текст с помощью HTML. "
                "Не используй Markdown. Немного разбавь текст эмодзи, но не перебарщивай.""Не используй двойной enter ля разделения строк, текст должен быть читаемым")
    elif role_key == "teacher":
        return ("Ты — учитель, который объясняет сложные темы простыми словами и помогает учиться. "
                "Отвечай понятно и дружелюбно.""Отвечай кратко, максимум 20 предложений, без лишнего текста. Форматируй текст с помощью HTML. "
                "Не используй Markdown. Немного разбавь текст эмодзи, но не перебарщивай.""Не используй двойной enter ля разделения строк, текст должен быть читаемым")
    elif role_key == "analyst":
        return ("Ты — аналитик, который делает логические выводы, анализирует информацию и даёт полезные советы. "
                "Будь точен и рассудителен.""Отвечай кратко, максимум 20 предложений, без лишнего текста. Форматируй текст с помощью HTML. "
                "Не используй Markdown. Немного разбавь текст эмодзи, но не перебарщивай.""Не используй двойной enter ля разделения строк, текст должен быть читаемым")
    else:
        return ("Отвечай кратко, максимум 20 предложений, без лишнего текста. Форматируй текст с помощью HTML. "
                "Не используй Markdown. Немного разбавь текст эмодзи, но не перебарщивай.""Не используй двойной enter ля разделения строк, текст должен быть читаемым")


async def chat_handler(message: types.Message):
    user_id = message.from_user.id
    model_name = user_models.get(user_id, MODELS["deepseek_v3"])
    role_key = user_roles.get(user_id, None)

    system_prompt = get_system_prompt(role_key)

    try:
        await message.answer("⏳ Подождите, ответ генерируется...")
        await message.bot(SendChatAction(chat_id=message.chat.id, action="typing"))

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message.text}
            ],
            max_tokens=5000
        )

        answer = response.choices[0].message.content
        cleaned_answer = clean_html(answer)
        await message.answer(cleaned_answer)

    except Exception as e:
        await message.answer(f"Произошла ошибка при запросе к API:\n{e}")


def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_models, Command("models"))
    dp.callback_query.register(set_model_callback, lambda c: c.data and c.data.startswith("set_model:"))
    dp.message.register(cmd_roles, Command("roles"))
    dp.callback_query.register(set_role_callback, lambda c: c.data and c.data.startswith("set_role:"))
    dp.message.register(chat_handler)
