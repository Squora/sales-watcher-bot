import json
import random

async def advertise_product(update, context):
    with open('data/products.json', 'r', encoding='utf-8') as f:
        all_products = json.load(f)

    filtered_products = all_products.copy()

    category = context.user_data.get("category")
    if category == "cheap":
        filtered_products = sorted(filtered_products, key=lambda x: x["price"])
    elif category == "brand_casio":
        filtered_products = [p for p in filtered_products if "casio" in p["name"].lower()]
    elif category in ["sport_watch", "business_watch", "mechanical_watch", "luxury_watch", "smart_watch"]:
        filtered_products = [p for p in filtered_products if category == p.get("category")]

    max_price = context.user_data.get("max_price")
    if max_price:
        filtered_products = [p for p in filtered_products if isinstance(p["price"], (int, float)) and p["price"] <= max_price]
    if not filtered_products:
        filtered_products = sorted(all_products, key=lambda x: x["price"])[:3]
        await update.message.reply_text("😕 Не нашли подходящих вариантов. Вот наши топ-предложения:")

    for product in filtered_products[:3]:
        name = product["name"]
        price = product["price"]
        description = product["description"]
        image = product.get("image")

        caption = f"<b>{name}</b>\nЦена: {price}₽\n{description}"

        if image:
            await update.message.reply_photo(photo=image, caption=caption, parse_mode='HTML')
        else:
            await update.message.reply_text(caption, parse_mode='HTML')

async def advertise_product_direct(chat_id, bot, user_data):
    with open('data/products.json', 'r', encoding='utf-8') as f:
        all_products = json.load(f)

    filtered_products = all_products.copy()

    # Фильтр по категории
    category = user_data.get("category")
    if category == "cheap":
        filtered_products = sorted(filtered_products, key=lambda x: x["price"])
    elif category == "brand_casio":
        filtered_products = [p for p in filtered_products if "casio" in p["name"].lower()]
    elif category in ["sport_watch", "business_watch", "mechanical_watch", "luxury_watch", "smart_watch"]:
        filtered_products = [p for p in filtered_products if category == p.get("category")]

    # Фильтр по бюджету
    max_price = user_data.get("max_price")
    if max_price:
        filtered_products = [p for p in filtered_products if isinstance(p["price"], (int, float)) and p["price"] <= max_price]

    # Если ничего не найдено — fallback
    if not filtered_products:
        filtered_products = sorted(all_products, key=lambda x: x["price"])[:3]
        await bot.send_message(chat_id=chat_id, text="😕 Не нашли подходящих вариантов. Вот наши топ-предложения:")

    # Выбираем 1 случайный товар
    product = random.choice(filtered_products)
    name = product["name"]
    price = product["price"]
    description = product["description"]
    image = product.get("image")

    caption = (
        f"🔥 <b>{name}</b> 🔥\n"
        f"💰 Всего за <b>{price}₽</b>!\n\n"
        f"{description}\n\n"
        f"📦 Осталось немного! Успей заказать сегодня!"
    )

    if image:
        await bot.send_photo(chat_id=chat_id, photo=image, caption=caption, parse_mode='HTML')
    else:
        await bot.send_message(chat_id=chat_id, text=caption, parse_mode='HTML')
