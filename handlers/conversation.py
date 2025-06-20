from handlers.product_advertising import advertise_product, advertise_product_direct
from intent_model import load_model
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime

from utils.logger import logger

model, vectorizer = load_model()
known_users = set()

reply_keyboard = [
    ["Спортивные", "Деловые", "Механические"],
    ["Недорогие", "Casio", "Посмотреть все"]
]
keyboard_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

async def chat(update, context, recognized_text=None):
    user_id = update.effective_chat.id
    known_users.add(user_id)
    logger.info(f"[{user_id}] Received message: {update.message.text}")
    user_message = recognized_text.lower() if recognized_text else update.message.text.lower()

    X = vectorizer.transform([user_message])
    intent = model.predict(X)[0]

    if intent == "greeting":
        context.user_data.clear()
        await update.message.reply_text(
            "Привет! Я помогу подобрать идеальные часы для вас. ⌚\n"
            "Для начала выберите тип часов:",
            reply_markup=keyboard_markup
        )
        context.user_data["awaiting_category"] = True
        return

    if context.user_data.get("awaiting_category"):
        text_to_key = {
            "спортивные": "sport_watch",
            "деловые": "business_watch",
            "механические": "mechanical_watch",
            "недорогие": "cheap",
            "casio": "brand_casio",
            "посмотреть все": "product"
        }
        selected = text_to_key.get(user_message)
        if selected:
            context.user_data["category"] = selected
            context.user_data["category_name"] = user_message
            context.user_data["awaiting_category"] = False
            context.user_data["awaiting_budget"] = True
            await update.message.reply_text(
                "Отлично! Теперь укажите ваш максимальный бюджет (например: 10000, 15000):",
                reply_markup=ReplyKeyboardRemove()
            )
            return

    if context.user_data.get("awaiting_budget"):
        try:
            budget = int(''.join(filter(str.isdigit, user_message)))
            context.user_data["max_price"] = budget
            context.user_data["awaiting_budget"] = False
            await update.message.reply_text(f"Ищем варианты до {budget}₽...")
            await advertise_product(update, context)
            return
        except:
            await update.message.reply_text("Пожалуйста, укажите бюджет цифрами (например: 10000).")
            return

    if intent == "product":
        await advertise_product(update, context)
        return

    if intent == "goodbye":
        await update.message.reply_text("До встречи! Буду рад снова помочь 🙂")
        return

    if intent == "time":
        now = datetime.now().strftime("%H:%M")
        await update.message.reply_text(f"Сейчас {now}")
        return

    keywords = {
        "вод": "водонепроницаемые",
        "пульс": "с пульсометром",
        "класс": "классические",
        "соврем": "современные",
        "авто": "с автоподзаводом",
        "ручн": "с ручным заводом"
    }

    if "category" in context.user_data:
        for word, feature in keywords.items():
            if word in user_message:
                context.user_data["feature"] = feature
                await update.message.reply_text(f"Учту ваше пожелание по {feature} функциям.")
                await advertise_product(update, context)
                return

    await update.message.reply_text(
        "Пожалуйста, выберите категорию часов, используя кнопки:",
        reply_markup=keyboard_markup
    )
    context.user_data["awaiting_category"] = True

async def send_periodic_advertisement(context):
    chat_id = context.job.chat_id
    user_data = {}

    await advertise_product_direct(chat_id, context.bot, user_data)
