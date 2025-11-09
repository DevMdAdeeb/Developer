from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded
from database import add_user, remove_user, get_user
import configparser
import os

# Dictionary to hold the state of the login process for each user
login_sessions = {}

config = configparser.ConfigParser()
config.read('config.ini')

API_ID = int(config['pyrogram']['api_id'])
API_HASH = config['pyrogram']['api_hash']

async def handle_login_steps(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in login_sessions:
        return

    state = login_sessions[user_id].get("state")

    if state == "awaiting_phone":
        await process_phone_number(client, message)
    elif state == "awaiting_code":
        await process_verification_code(client, message)
    elif state == "awaiting_password":
        await process_2fa_password(client, message)

async def start_login_process(client: Client, message: Message):
    user_id = message.from_user.id
    login_sessions[user_id] = {"state": "awaiting_phone"}
    await message.reply("يرجى إرسال رقم هاتفك مع الرمز الدولي (مثال: +1234567890).")

async def process_phone_number(client: Client, message: Message):
    user_id = message.from_user.id
    phone_number = message.text

    # Create a new user client instance
    user_client = Client(f"user_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)

    try:
        await user_client.connect()
        sent_code = await user_client.send_code(phone_number)

        login_sessions[user_id].update({
            "phone": phone_number,
            "phone_code_hash": sent_code.phone_code_hash,
            "state": "awaiting_code",
            "client": user_client
        })

        await message.reply("تم إرسال رمز التحقق. يرجى إرساله الآن.")
    except Exception as e:
        await message.reply(f"حدث خطأ: {e}")
        del login_sessions[user_id]

async def process_verification_code(client: Client, message: Message):
    user_id = message.from_user.id
    code = message.text
    session_data = login_sessions[user_id]
    user_client = session_data["client"]

    try:
        await user_client.sign_in(session_data["phone"], session_data["phone_code_hash"], code)

        # Successfully logged in
        session_string = await user_client.export_session_string()
        add_user(user_id, session_data["phone"], session_string)

        await message.reply("تم تسجيل الدخول بنجاح!")
        await user_client.disconnect()
        del login_sessions[user_id]

    except SessionPasswordNeeded:
        login_sessions[user_id]["state"] = "awaiting_password"
        await message.reply("حسابك محمي بكلمة مرور التحقق بخطوتين. يرجى إرسالها.")
    except Exception as e:
        await message.reply(f"حدث خطأ: {e}")
        await user_client.disconnect()
        del login_sessions[user_id]

async def process_2fa_password(client: Client, message: Message):
    user_id = message.from_user.id
    password = message.text
    session_data = login_sessions[user_id]
    user_client = session_data["client"]

    try:
        await user_client.check_password(password)

        # Successfully logged in with 2FA
        session_string = await user_client.export_session_string()
        add_user(user_id, session_data["phone"], session_string)

        await message.reply("تم تسجيل الدخول بنجاح!")

    except Exception as e:
        await message.reply(f"حدث خطأ: {e}")
    finally:
        await user_client.disconnect()
        del login_sessions[user_id]

async def logout(client: Client, message: Message):
    user_id = message.from_user.id
    if get_user(user_id):
        # Remove the session file if it exists
        session_file = f"user_{user_id}.session"
        if os.path.exists(session_file):
            os.remove(session_file)

        remove_user(user_id)
        await message.reply("تم تسجيل الخروج بنجاح وحذف جميع بياناتك.")
    else:
        await message.reply("أنت غير مسجل دخول بالفعل.")
