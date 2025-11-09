from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database import get_user
from handlers.auth import start_login_process, logout

# Main menu keyboard
main_menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("تسجيل حساب جديد"), KeyboardButton("تسجيل الخروج")],
        [KeyboardButton("فحص اليوزرات")]
    ],
    resize_keyboard=True
)

async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    if get_user(user_id):
        welcome_text = "أهلاً بك مجدداً! اختر أحد الخيارات من القائمة."
    else:
        welcome_text = "أهلاً بك في بوت فحص اليوزرات! يرجى تسجيل حساب جديد للبدء."

    await message.reply(welcome_text, reply_markup=main_menu)

async def handle_text_buttons(client: Client, message: Message):
    text = message.text

    if text == "تسجيل حساب جديد":
        await start_login_process(client, message)
    elif text == "تسجيل الخروج":
        await logout(client, message)
    elif text == "فحص اليوزرات":
        # This will be handled by the checker module
        # We need to import and call the function from there
        from handlers.checker import start_checking
        await start_checking(client, message)
    else:
        # Handle other text messages, potentially part of the login flow
        from handlers.auth import handle_login_steps
        await handle_login_steps(client, message)
