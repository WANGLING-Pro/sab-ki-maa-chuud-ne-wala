import threading
import os

from click_counter import click_app

from bot import Bot

def run_flask():
port = int(os.getenv("PORT", 8000))
click_app.run(host="0.0.0.0", port=port)

def run_bot():
bot = Bot()
bot.run()

if name == "main":
t = threading.Thread(target=run_flask)
t.start()
run_bot()

main.py hai
