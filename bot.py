import asyncio
import os
import nest_asyncio

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

nest_asyncio.apply()

TOKEN = os.environ["TOKEN"]

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 پیام شما دریافت شد.")

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    )

    print("ربات روشن شد 🤖")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
