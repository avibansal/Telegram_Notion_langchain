import os
from dotenv import load_dotenv
load_dotenv()

import base64
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from core.llm import run_agent

# ── Configuration ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ── Handlers ───────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    welcome = (
        "👋 *Welcome to the Notion Task Manager Bot!*\n\n"
        "I can help you manage your Notion tasks. Try:\n"
        "• _Show me all tasks_\n"
        "• _What are today's tasks?_\n"
        "• _Add a task called 'Meeting' for 2026-02-20_\n"
        "• _Update the 'Meeting' task to Done_\n"
        "• _Give me a task summary_\n"
        "• Send a photo and I'll analyze it!\n\n"
        "Just type a message and I'll handle it! 🚀"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward every text message to the LLM agent and reply with its response."""
    user_text = update.message.text
    logger.info("User %s: %s", update.effective_user.first_name, user_text)

    await update.message.chat.send_action("typing")

    try:
        response = run_agent(user_text)
    except Exception as e:
        logger.error("Agent error: %s", e)
        response = f"⚠️ Something went wrong:\n`{e}`"

    try:
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(response)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages — save directly to Notion Images Dump page."""
    caption = update.message.caption or ""
    logger.info("User %s sent a photo: %s", update.effective_user.first_name, caption)

    await update.message.chat.send_action("typing")

    try:
        # Get the highest resolution photo and its public URL
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_url = file.file_path

        # Save directly to Notion (no LLM needed)
        from core.langchain_tool import dump_image
        result = dump_image.invoke({"image_url": image_url, "caption": caption})
        response = f"Saved to Notion!\n{caption}" if caption else "Image saved to Notion!"
    except Exception as e:
        logger.error("Agent error (photo): %s", e)
        response = f"Something went wrong: {e}"

    await update.message.reply_text(response)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error("Update %s caused error: %s", update, context.error)


# ── Main ───────────────────────────────────────────────────────
def main():
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please set your Telegram bot token!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_error_handler(error_handler)

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()