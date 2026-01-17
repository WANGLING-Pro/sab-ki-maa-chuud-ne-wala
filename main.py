import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bot import Bot

class Dummy(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy():
    HTTPServer(("0.0.0.0", 8000), Dummy).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_dummy).start()
    Bot().run()
