import threading
import os
from click_counter import click_app
from bot import Bot

def run_flask():
    # Flask ko Render ke PORT pe chalne do
    port = int(os.getenv("PORT", 10000))
    click_app.run(host="0.0.0.0", port=port)

def run_bot():
    # Bot ko background me run hone do (Flask ke port ko use nahi karega)
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    # Flask ko ek alag thread me start karo
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Bot ko main thread me run hone do
    run_bot()
