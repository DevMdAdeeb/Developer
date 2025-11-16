import schedule
import time
import threading
import logging
import asyncio
from telegram.ext import Application, CommandHandler
from data_fetcher import get_data
from technical_analyzer import analyze_data
from bot import (
    TELEGRAM_TOKEN,
    load_subscribers,
    start_command,
    stop_command,
    help_command
)

# --- Configuration ---
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']
TIMEFRAMES = ['15m', '1h', '2h', '4h']

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Global Application and Event Loop Objects ---
app = None
loop = None

# --- Core Logic ---
def check_signals():
    """Iterates through symbols and timeframes, fetches data, analyzes it, and triggers notifications."""
    logger.info("Scheduler is running signal check...")
    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            try:
                logger.info(f"Checking {symbol} on {timeframe}...")
                market_data = get_data(symbol, timeframe)
                if market_data is not None and not market_data.empty:
                    signal_found = analyze_data(market_data)
                    if signal_found:
                        message = f"🚨 إشارة شراء محتملة! 🚨\n\n" \
                                  f"العملة: {symbol}\n" \
                                  f"الإطار الزمني: {timeframe}"
                        logger.info(f"Signal found for {symbol} on {timeframe}. Broadcasting...")
                        if loop:
                            asyncio.run_coroutine_threadsafe(broadcast(message), loop)
                else:
                    logger.warning(f"Could not get data for {symbol} on {timeframe}.")
                time.sleep(2) # To avoid hitting API rate limits
            except Exception as e:
                logger.error(f"Error checking signal for {symbol} on {timeframe}: {e}")
    logger.info("Signal check finished.")

async def broadcast(message):
    """Sends a message to all subscribers."""
    subscribers = load_subscribers()
    if not subscribers:
        logger.info("Broadcast skipped: No subscribers.")
        return

    for chat_id in subscribers:
        try:
            await app.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")

# --- Bot and Scheduler Setup ---
def run_bot():
    """Sets up and runs the Telegram bot in polling mode."""
    global app, loop
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_TOKEN":
        logger.error("Please replace 'YOUR_TELEGRAM_TOKEN' in the bot.py file.")
        return

    loop = asyncio.get_event_loop()

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler(["start", "subscribe"], start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))

    logger.info("Telegram Bot is starting...")
    app.run_polling()

def run_scheduler():
    """Sets up and runs the job scheduler."""
    logger.info("Scheduler is starting...")
    schedule.every(15).minutes.do(check_signals)
    check_signals() # Run once at startup
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- Main Execution ---
if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    run_scheduler()
