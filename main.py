import threading
import os
from flask import Flask
from bot import Bot

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
