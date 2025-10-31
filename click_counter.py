# ============================================================== #
# ✅ FLASK CLICK COUNTER — Redirect pe MongoDB clicks update
# ============================================================== #

#  CLICK COUNTER API — v3.0

from flask import Flask, request, redirect
from pymongo import MongoClient
from urllib.parse import quote, unquote
import os

click_app = Flask(__name__)

# ==================== ⚙️ MongoDB Connection ==================== #
mongo_url = os.getenv("MONGODB_URL")
if not mongo_url:
    raise ValueError("⚠️ Missing MONGODB_URL environment variable!")

mongo = MongoClient(mongo_url)
db = mongo["botdb"]
clicks = db["clicks"]

# ==================== 🎯 Redirect Endpoint ==================== #
@click_app.route("/redirect")
def redirect_link():
    try:
        user_id = request.args.get("user_id")
        target = request.args.get("link")

        if not user_id or not target:
            return "Missing parameters: user_id and link", 400

        try:
            user_id = int(user_id)
        except ValueError:
            return "Invalid user_id format", 400

        # Decode target link (Telegram start link)
        target = unquote(target)

        # Increment user click count
        clicks.update_one(
            {"user_id": user_id},
            {"$inc": {"clicks": 1}},
            upsert=True
        )

        # Redirect user to Telegram start link
        return f"""
        <html>
            <head>
                <meta http-equiv="refresh" content="0; url={target}" />
            </head>
            <body>
                <p>Redirecting... Please wait.</p>
            </body>
        </html>
        """

    except Exception as e:
        return f"Error: {e}", 500


# ==================== 🩵 Health Check Route ==================== #
@click_app.route("/")
def home():
    return "✅ Click Counter API Active — Ready to track user clicks!"


# ==================== 📊 Stats Route (Optional Debug) ==================== #
@click_app.route("/stats")
def show_stats():
    try:
        data = list(clicks.find({}, {"_id": 0}))
        total = len(data)
        return {"total_users": total, "data": data}
    except Exception as e:
        return {"error": str(e)}, 500

@click_app.route("/get_clicks")
def get_clicks():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return {"error": "user_id required"}, 400

        data = clicks.find_one({"user_id": int(user_id)}, {"_id": 0, "clicks": 1})
        total_clicks = data["clicks"] if data else 0
        return {"total_clicks": total_clicks}, 200

    except Exception as e:
        return {"error": str(e)}, 500

# ================================================================== #
# 🏁 End of File — click Counter. — More New future Coming soon
# ================================================================== #
