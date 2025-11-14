import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Configuration ---
# PLEASE REPLACE "YOUR_TELEGRAM_TOKEN" WITH YOUR ACTUAL BOT TOKEN
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
SUBSCRIBERS_FILE = 'subscribers.json'

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Subscriber Management ---
def load_subscribers():
    """Loads the list of subscriber chat IDs from the JSON file."""
    try:
        with open(SUBSCRIBERS_FILE, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_subscribers(subscribers):
    """Saves the list of subscriber chat IDs to the JSON file."""
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(list(subscribers), f)

# --- Bot Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start and /subscribe commands."""
    chat_id = update.message.chat_id
    subscribers = load_subscribers()
    if chat_id not in subscribers:
        subscribers.add(chat_id)
        save_subscribers(subscribers)
        await update.message.reply_text("أهلاً بك! تم اشتراكك بنجاح في إشعارات البوت. سيتم إعلامك عند ظهور أي إشارة جديدة.")
    else:
        await update.message.reply_text("أنت مشترك بالفعل!")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /stop command."""
    chat_id = update.message.chat_id
    subscribers = load_subscribers()
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        save_subscribers(subscribers)
        await update.message.reply_text("تم إلغاء اشتراكك. لن تتلقى المزيد من الإشعارات.")
    else:
        await update.message.reply_text("أنت لست مشتركًا.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    help_text = (
        "هذا البوت يقوم بمراقبة أسواق العملات الرقمية ويرسل إشعارًا عند تحقق شروط فنية معينة.\n\n"
        "الأوامر المتاحة:\n"
        "/start أو /subscribe - لبدء البوت والاشتراك في الإشعارات.\n"
        "/stop - لإلغاء الاشتراك في الإشعارات."
    )
    await update.message.reply_text(help_text)

# --- Main Application ---
def main():
    """Sets up and runs the Telegram bot."""
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_TOKEN":
        logger.warning("Please replace 'YOUR_TELEGRAM_TOKEN' in the bot.py file with your actual bot token.")
        return

    # Create the Application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler(["start", "subscribe"], start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))

    # This function will be needed in the main script to send notifications.
    # We are not using it here, but it's part of the bot's logic.
    async def broadcast(message):
        subscribers = load_subscribers()
        for chat_id in subscribers:
            try:
                await app.bot.send_message(chat_id=chat_id, text=message)
            except Exception as e:
                logger.error(f"Failed to send message to {chat_id}: {e}")

    logger.info("Bot is starting...")
    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    # This file defines the bot's logic. It is not meant to be run directly on its own
    # in the final application, but will be integrated into the main script.
    # The 'main()' function is provided to allow for testing the bot independently.
    print("Bot logic file created. This file should be imported, not run directly in the final app.")
    # To test this file alone, you would replace the token and call main()
    # main()
