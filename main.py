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

# --- الإعدادات ---
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']
TIMEFRAMES = ['15m', '1h', '2h', '4h']

# --- إعدادات تسجيل الأنشطة ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- متغيرات التطبيق وحلقة الأحداث ---
app = None
loop = None

# --- المنطق الأساسي ---
def check_signals():
    """يتكرر عبر الرموز والأطر الزمنية، يجلب البيانات، يحللها، ويرسل الإشعارات."""
    logger.info("الجدول الزمني يقوم بفحص الإشارات...")
    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            try:
                logger.info(f"يتم فحص {symbol} على إطار زمني {timeframe}...")
                market_data = get_data(symbol, timeframe)
                if market_data is not None and not market_data.empty:
                    signal_found = analyze_data(market_data)
                    if signal_found:
                        message = f"🚨 إشارة شراء محتملة! 🚨\n\n" \
                                  f"العملة: {symbol}\n" \
                                  f"الإطار الزمني: {timeframe}"
                        logger.info(f"تم العثور على إشارة لـ {symbol} على إطار زمني {timeframe}. يتم الآن الإرسال...")
                        if loop:
                            asyncio.run_coroutine_threadsafe(broadcast(message), loop)
                else:
                    logger.warning(f"لم يتم الحصول على بيانات لـ {symbol} على إطار زمني {timeframe}.")
                time.sleep(2) # لتجنب الوصول إلى حدود طلبات API
            except Exception as e:
                logger.error(f"خطأ أثناء فحص الإشارة لـ {symbol} على إطار زمني {timeframe}: {e}")
    logger.info("انتهى فحص الإشارات.")

async def broadcast(message):
    """يرسل رسالة إلى جميع المشتركين."""
    subscribers = load_subscribers()
    if not subscribers:
        logger.info("تم تخطي الإرسال: لا يوجد مشتركين.")
        return

    for chat_id in subscribers:
        try:
            await app.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"فشل إرسال الرسالة إلى {chat_id}: {e}")

# --- إعداد البوت والجدول الزمني ---
def run_bot():
    """يقوم بإعداد وتشغيل بوت التلغرام."""
    global app, loop
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_TOKEN":
        logger.error("يرجى استبدال 'YOUR_TELEGRAM_TOKEN' في ملف bot.py.")
        return

    loop = asyncio.get_event_loop()

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler(["start", "subscribe"], start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))

    logger.info("بوت التلغرام قيد التشغيل...")
    app.run_polling()

def run_scheduler():
    """يقوم بإعداد وتشغيل جدول المهام."""
    logger.info("الجدول الزمني قيد التشغيل...")
    schedule.every(15).minutes.do(check_signals)
    check_signals() # التشغيل مرة واحدة عند بدء التشغيل
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- التنفيذ الرئيسي ---
if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    run_scheduler()
