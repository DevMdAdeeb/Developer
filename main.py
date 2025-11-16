import logging
import asyncio
import aioschedule as schedule
from telegram.ext import Application, CommandHandler

from data_fetcher import get_data
from technical_analyzer import analyze_data
from bot import (
    TELEGRAM_TOKEN,
    load_subscribers,
    start_command,
    stop_command,
    help_command,
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

# --- متغير التطبيق العالمي ---
# نحتاج أن يكون هذا المتغير قابلاً للوصول من قبل دالة الإرسال
app: Application = None

# --- المنطق الأساسي ---
async def broadcast(message: str):
    """يرسل رسالة إلى جميع المشتركين."""
    subscribers = load_subscribers()
    if not subscribers:
        logger.info("تم تخطي الإرسال: لا يوجد مشتركين.")
        return

    for chat_id in subscribers:
        try:
            # استخدم `app.bot` الذي تم إنشاؤه في `main`
            await app.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"فشل إرسال الرسالة إلى {chat_id}: {e}")

async def check_signals():
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
                        message = (
                            f"🚨 إشارة شراء محتملة! 🚨\n\n"
                            f"العملة: {symbol}\n"
                            f"الإطار الزمني: {timeframe}"
                        )
                        logger.info(f"تم العثور على إشارة لـ {symbol} على إطار زمني {timeframe}. يتم الآن الإرسال...")
                        await broadcast(message)
                else:
                    logger.warning(f"لم يتم الحصول على بيانات لـ {symbol} على إطار زمني {timeframe}.")
                await asyncio.sleep(2) # لتجنب الوصول إلى حدود طلبات API
            except Exception as e:
                logger.error(f"خطأ أثناء فحص الإشارة لـ {symbol} على إطار زمني {timeframe}: {e}")
    logger.info("انتهى فحص الإشارات.")

async def run_scheduler():
    """يقوم بتشغيل المهام المجدولة بشكل مستمر."""
    await check_signals() # التشغيل مرة واحدة عند بدء التشغيل
    schedule.every(15).minutes.do(check_signals)
    logger.info("الجدول الزمني قيد التشغيل...")
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    """يقوم بإعداد وتشغيل بوت التلغرام والجدول الزمني بشكل متزامن."""
    global app
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_TELEGRAM_TOKEN":
        logger.error("يرجى وضع توكن التلغرام الصحيح في ملف token.txt.")
        return

    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # إضافة معالجات الأوامر
    app.add_handler(CommandHandler(["start", "subscribe"], start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))

    logger.info("يتم الآن بدء تشغيل البوت والجدول الزمني...")

    # تشغيل البوت والجدول الزمني معًا
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        # الآن بعد أن بدأ البوت، يمكننا تشغيل الجدول الزمني إلى الأبد
        await run_scheduler()
    finally:
        # إيقاف البوت بأناقة عند الخروج
        await app.updater.stop()
        await app.stop()


# --- التنفيذ الرئيسي ---
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت يدويًا.")
