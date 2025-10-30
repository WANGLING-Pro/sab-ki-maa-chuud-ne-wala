from click_counter import click_app
from bot import Bot
import threading, os

def run_flask():
    port = int(os.getenv("PORT", 10000))  # Render ka PORT variable use kare
    click_app.run(host="0.0.0.0", port=port)

def run_bot():
    Bot().run()

if __name__ == "__main__":
    # Flask aur bot dono ko parallel run karna
    t1 = threading.Thread(target=run_flask)
    t1.start()

    run_bot()
