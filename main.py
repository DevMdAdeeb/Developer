import configparser
from pyrogram import Client, filters

from database import init_db
from handlers.start import start_command, handle_text_buttons
from handlers.checker import stop_checking_callback

def main():
    # Read configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    API_ID = config.getint('pyrogram', 'api_id')
    API_HASH = config.get('pyrogram', 'api_hash')
    BOT_TOKEN = config.get('pyrogram', 'bot_token')

    # Initialize the database
    init_db()

    # Initialize the bot
    app = Client(
        "username_checker_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    # Register handlers
    app.add_handler(filters.command("start")(start_command))
    app.add_handler(filters.text(handle_text_buttons))
    app.add_handler(filters.regex("stop_checking")(stop_checking_callback))

    # Start the bot
    print("Bot is starting...")
    app.run()
    print("Bot has stopped.")

if __name__ == "__main__":
    main()
