import string
import asyncio
import itertools
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UsernameNotOccupied, UsernameInvalid
from database import get_user
import configparser

# --- Globals & Config ---

# Dictionary to control the checking status for each user
checking_status = {}

config = configparser.ConfigParser()
config.read('config.ini')
API_ID = int(config['pyrogram']['api_id'])
API_HASH = config['pyrogram']['api_hash']
BOT_USERNAME = config['pyrogram']['bot_username']

# --- Helper Functions ---

def generate_usernames():
    """Generator for unique usernames based on specified patterns."""
    letters = string.ascii_lowercase
    digits = string.digits

    patterns = [
        itertools.product(letters, repeat=3),                             # l_l_l
        itertools.product(letters, letters, digits),                       # l_l_d
        itertools.product(letters, digits, letters),                       # l_d_l
        itertools.product(letters, digits, digits)                         # l_d_d
    ]

    for pattern in patterns:
        for item in pattern:
            # This ensures the first item is always a letter as per the structure
            first, second, third = item[0], item[1], item[2]
            yield f"{first}_{second}_{third}"


async def start_checking(bot: Client, message: Message):
    """Starts the username checking process for a user."""
    user_id = message.from_user.id
    user_data = get_user(user_id)

    if not user_data:
        await message.reply("يجب عليك تسجيل الدخول أولاً. استخدم زر 'تسجيل حساب جديد'.")
        return

    if checking_status.get(user_id):
        await message.reply("عملية الفحص جارية بالفعل.")
        return

    checking_status[user_id] = True
    asyncio.create_task(run_checker(bot, message, user_data))


async def run_checker(bot: Client, message: Message, user_data):
    """The main coroutine that performs the username checking."""
    user_id = message.from_user.id
    _, phone_number, session_string = user_data

    status_message = await message.reply("⏳ جارِ تهيئة الفحص...")
    user_client = Client(f"user_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=session_string)

    try:
        await user_client.connect()
    except Exception as e:
        await status_message.edit(f"فشل الاتصال بحسابك: {e}\nيرجى تسجيل الخروج ثم الدخول مرة أخرى.")
        checking_status[user_id] = False
        return

    available_count = 0
    stop_button = InlineKeyboardMarkup([[InlineKeyboardButton("إيقاف الفحص", callback_data="stop_checking")]])

    for username in generate_usernames():
        if not checking_status.get(user_id):
            await status_message.edit("تم إيقاف الفحص من قبل المستخدم.")
            break

        status_text = (
            f"**🔎 جاري الفحص...**\n\n"
            f"👤 **الحساب:** `{phone_number}`\n"
            f"📝 **اليوزر الحالي:** `@{username}`\n"
            f"✅ **المتاحة:** `{available_count}`\n"
            f"**النمط:** ثلاثي"
        )
        try:
            await status_message.edit(status_text, reply_markup=stop_button)
        except FloodWait as e:
            await asyncio.sleep(e.x)

        try:
            await user_client.get_chat(username)
        except (UsernameNotOccupied, UsernameInvalid):
            available_count += 1
            await bot.send_message(user_id, f"✅ يوزر متاح: @{username}")
            try:
                new_channel = await user_client.create_channel(title=username, description=f"Reserved by @{BOT_USERNAME}")
                await user_client.set_chat_username(new_channel.id, username)
                await bot.send_message(user_id, f"🎉 تم حجز اليوزر @{username} في قناة خاصة بنجاح!")
            except Exception as e:
                await bot.send_message(user_id, f"⚠️ فشل حجز اليوزر @{username}. الخطأ: {e}")
        except FloodWait as e:
            await bot.send_message(user_id, f"تم تقييد حسابك مؤقتاً لمدة {e.x} ثانية. سيتم استئناف الفحص بعدها.")
            await asyncio.sleep(e.x)
        except Exception:
            pass # Ignore other errors like ChannelPrivate etc.

        await asyncio.sleep(3)

    else:
        await status_message.edit("اكتمل فحص جميع اليوزرات.")

    await user_client.disconnect()
    checking_status[user_id] = False


async def stop_checking_callback(bot: Client, callback_query):
    """Callback handler to stop the checking process."""
    user_id = callback_query.from_user.id
    if checking_status.get(user_id):
        checking_status[user_id] = False
        await callback_query.answer("تم إرسال طلب الإيقاف. ستتوقف العملية قريباً.", show_alert=True)
    else:
        await callback_query.answer("لا توجد عملية فحص جارية لإيقافها.", show_alert=True)
