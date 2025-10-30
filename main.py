from threading import Thread
from click_counter import click_app
from bot import Bot
import pyrogram.utils

pyrogram.utils.MIN_CHANNEL_ID = -1002917577512

if __name__ == "__main__":
    # Flask app ko background me run karna
    Thread(target=lambda: click_app.run(host="0.0.0.0", port=8080)).start()

    # Telegram bot run karna
    Bot().run()
