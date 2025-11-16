import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- الإعدادات ---
def load_token():
    """تحميل توكن البوت من ملف token.txt."""
    try:
        with open('token.txt', 'r') as f:
            token = f.read().strip()
            if not token:
                logging.error("ملف token.txt فارغ. يرجى وضع التوكن الخاص بك فيه.")
                return None
            return token
    except FileNotFoundError:
        logging.error("ملف token.txt غير موجود. يرجى إنشاء الملف ووضع التوكن الخاص بك فيه.")
        return None

# تحميل التوكن
TELEGRAM_TOKEN = load_token()
SUBSCRIBERS_FILE = 'subscribers.json'


# --- إعدادات تسجيل الأنشطة ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- إدارة المشتركين ---
def load_subscribers():
    """تحميل قائمة معرفات الدردشة للمشتركين من ملف JSON."""
    try:
        with open(SUBSCRIBERS_FILE, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_subscribers(subscribers):
    """حفظ قائمة معرفات الدردشة للمشتركين في ملف JSON."""
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(list(subscribers), f)

# --- معالجات أوامر البوت ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أوامر /start و /subscribe."""
    chat_id = update.message.chat_id
    subscribers = load_subscribers()
    if chat_id not in subscribers:
        subscribers.add(chat_id)
        save_subscribers(subscribers)
        await update.message.reply_text("أهلاً بك! تم اشتراكك بنجاح في إشعارات البوت. سيتم إعلامك عند ظهور أي إشارة جديدة.")
    else:
        await update.message.reply_text("أنت مشترك بالفعل!")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر /stop."""
    chat_id = update.message.chat_id
    subscribers = load_subscribers()
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        save_subscribers(subscribers)
        await update.message.reply_text("تم إلغاء اشتراكك. لن تتلقى المزيد من الإشعارات.")
    else:
        await update.message.reply_text("أنت لست مشتركًا.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر /help."""
    help_text = (
        "هذا البوت يقوم بمراقبة أسواق العملات الرقمية ويرسل إشعارًا عند تحقق شروط فنية معينة.\n\n"
        "الأوامر المتاحة:\n"
        "/start أو /subscribe - لبدء البوت والاشتراك في الإشعارات.\n"
        "/stop - لإلغاء الاشتراك في الإشعارات."
    )
    await update.message.reply_text(help_text)

# --- التطبيق الرئيسي ---
def main():
    """إعداد وتشغيل بوت التلغرام."""
    if not TELEGRAM_TOKEN:
        logger.error("لم يتم العثور على توكن التلغرام. يرجى التأكد من وجود ملف token.txt يحتوي على التوكن.")
        return

    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # إضافة معالجات الأوامر
    app.add_handler(CommandHandler(["start", "subscribe"], start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))

    # هذه الدالة ستكون ضرورية في السكربت الرئيسي لإرسال الإشعارات.
    # لا نستخدمها هنا، ولكنها جزء من منطق البوت.
    async def broadcast(message):
        subscribers = load_subscribers()
        for chat_id in subscribers:
            try:
                await app.bot.send_message(chat_id=chat_id, text=message)
            except Exception as e:
                logger.error(f"فشل إرسال الرسالة إلى {chat_id}: {e}")

    logger.info("البوت قيد التشغيل...")
    # بدء تشغيل البوت
    app.run_polling()

if __name__ == '__main__':
    # هذا الملف يحدد منطق البوت. ليس من المفترض تشغيله مباشرة بمفرده
    # في التطبيق النهائي، ولكن سيتم دمجه في السكربت الرئيسي.
    # تم توفير دالة 'main()' للسماح باختبار البوت بشكل مستقل.
    print("تم إنشاء ملف منطق البوت. يجب استيراد هذا الملف، وليس تشغيله مباشرة في التطبيق النهائي.")
    # لاختبار هذا الملف وحده، يمكنك استبدال التوكن واستدعاء main()
    # main()
