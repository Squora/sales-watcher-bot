import asyncio
import datetime

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import start, conversation, voice_handler
import config
from utils.logger import logger


def main():
    async def on_start(app):
        logger.info("Bot started.")
        asyncio.create_task(periodic_advertisement_task(app))

    app = ApplicationBuilder().token(config.BOT_TOKEN).post_init(on_start).build()

    app.add_handler(CommandHandler("start", start.start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler.handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversation.chat))

    app.run_polling()

async def periodic_advertisement_task(app):
    while True:
        for chat_id in conversation.known_users:
            app.job_queue.run_once(
                conversation.send_periodic_advertisement,
                when=datetime.timedelta(seconds=1),
                chat_id=chat_id,
                name=f"periodic_ad_{chat_id}"
            )
        await asyncio.sleep(600)

if __name__ == '__main__':
    main()
