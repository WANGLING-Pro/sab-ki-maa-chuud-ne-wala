from click_counter import click_app
from bot import Bot
import threading

def run_flask():
    # Flask app ko alag port (8080) pe run karte hain
    click_app.run(host="0.0.0.0", port=8080)

def run_bot():
    Bot().run()

if __name__ == "__main__":
    # Flask ko background thread me start kar do
    t1 = threading.Thread(target=run_flask)
    t1.start()

    # Ab bot run hoga
    run_bot()
