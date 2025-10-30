# ============================================================== #
# ✅ FLASK CLICK COUNTER — Redirect pe MongoDB clicks update
# ============================================================== #

from flask import Flask, request, redirect
from pymongo import MongoClient, ASCENDING
from urllib.parse import urlparse
import os
import logging

click_app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("click-counter")

mongo_url = os.getenv("MONGODB_URL")
if not mongo_url:
    raise ValueError("MONGODB_URL environment variable not found!")

mongo = MongoClient(mongo_url)
db = mongo["botdb"]
clicks = db["clicks"]
clicks.create_index([("user_id", ASCENDING)], unique=True)

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_HOSTS = set(os.getenv("ALLOWED_REDIRECT_HOSTS", "").split(",")) if os.getenv("ALLOWED_REDIRECT_HOSTS") else None

def is_safe_url(u: str) -> bool:
    try:
        p = urlparse(u)
        if p.scheme not in ALLOWED_SCHEMES or not p.netloc:
            return False
        if ALLOWED_HOSTS is not None and p.hostname not in ALLOWED_HOSTS:
            return False
        return True
    except Exception:
        return False

@click_app.route("/redirect")
def redirect_link():
    try:
        user_id = request.args.get("user_id")
        target = request.args.get("link")

        if not user_id or not target:
            return "Missing parameters: 'user_id' and 'link' are required", 400

        try:
            user_id = int(user_id)
        except ValueError:
            return "Invalid user_id. Must be integer.", 400

        if not is_safe_url(target):
            return "Invalid or disallowed redirect URL.", 400

        clicks.update_one({"user_id": user_id}, {"$inc": {"clicks": 1}}, upsert=True)
        return redirect(target, code=302)

    except Exception:
        logger.exception("Redirect processing failed")
        return "Internal Server Error", 500

@click_app.route("/")
def home():
    return "✅ Click Counter API Active — Ready to track user clicks!"


# ================================================================== #
# 🏁 End of File — click Counter. — More New future Coming soon
# ================================================================== #
