# ============================================================== #
# ✅ FLASK CLICK COUNTER — Redirect pe MongoDB clicks update (FIXED)
# ============================================================== #

from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient
from urllib.parse import unquote
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

        # ✅ Increment only on real browser visit
        # Add a simple header-based filter to prevent bot/script hits
        user_agent = request.headers.get("User-Agent", "").lower()
        if "telegram" not in user_agent:  # avoid Telegram preview hits
            clicks.update_one(
                {"user_id": user_id},
                {"$inc": {"clicks": 1}},
                upsert=True
            )

        target = unquote(target)
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


# ==================== 🩵 Health Check ==================== #
@click_app.route("/")
def home():
    return "✅ Click Counter API Active — Ready to track real user clicks!"


# ==================== 📊 Get User Clicks ==================== #
@click_app.route("/get_clicks")
def get_clicks():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id required"}), 400

        data = clicks.find_one({"user_id": int(user_id)}, {"_id": 0, "clicks": 1})
        total_clicks = data["clicks"] if data else 0
        return jsonify({"total_clicks": total_clicks}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 📊 Stats (for Debug/Admin only) ==================== #
@click_app.route("/stats")
def show_stats():
    try:
        data = list(clicks.find({}, {"_id": 0}))
        data.sort(key=lambda x: -x.get("clicks", 0))
        total = len(data)
        return jsonify({"total_users": total, "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================================================== #
# 🏁 End of File — Click Counter (Fixed for Telegram Bots)
# ================================================================== #
