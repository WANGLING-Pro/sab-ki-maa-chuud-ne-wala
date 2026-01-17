import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from bot import Bot

# -----------------------------
# Dummy HTTP Server
# -----------------------------
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running.")

def run_http():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Dummy HTTP server running on port {port}")
    server.serve_forever()

# -----------------------------
# Run Bot
# -----------------------------
def run_bot():
    bot = Bot()
    bot.run()

# -----------------------------
# Start Both
# -----------------------------
if __name__ == "__main__":
    t = threading.Thread(target=run_http)
    t.start()

    run_bot()
