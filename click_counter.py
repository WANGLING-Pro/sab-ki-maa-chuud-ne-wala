# ============================================================== #
# ✅ FLASK CLICK COUNTER — Each Link Has Separate Click Counter
# ============================================================== #

from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient
from urllib.parse import unquote
import os, hashlib

click_app = Flask(__name__)

# ==================== ⚙️ MongoDB Connection ==================== #
mongo_url = os.getenv("MONGODB_URL")
if not mongo_url:
    raise ValueError("⚠️ Missing MONGODB_URL environment variable!")

mongo = MongoClient(mongo_url)
db = mongo["botdb"]
clicks = db["clicks"]  # collection name


# ==================== 🎯 Redirect Endpoint ==================== #
@click_app.route("/redirect")
def redirect_link():
    try:
        user_id = request.args.get("user_id")
        target = request.args.get("link")

        if not user_id or not target:
            return "Missing parameters: user_id and link", 400

        user_id = int(user_id)
        target = unquote(target)

        # ✅ Unique link ID for every Telegram link
        link_id = hashlib.md5(target.encode()).hexdigest()

        # ✅ Avoid Telegram preview & bot clicks
        user_agent = request.headers.get("User-Agent", "").lower()
        if all(x not in user_agent for x in ["telegram", "bot", "preview"]):
            clicks.update_one(
                {"user_id": user_id, "link_id": link_id},
                {"$inc": {"clicks": 1}},
                upsert=True
            )

        # ✅ Redirect user properly
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
@click_app.route("/", endpoint="click_counter_home")
def click_counter_home():
    return "✅ Click Counter API Active — Link-wise tracking ready!"


# ==================== 📊 Get Clicks for Specific Link ==================== #
@click_app.route("/get_clicks", endpoint="click_counter_get_clicks")
def click_counter_get_clicks():
    try:
        user_id = request.args.get("user_id")
        link = request.args.get("link")

        if not user_id or not link:
            return jsonify({"error": "user_id and link required"}), 400

        user_id = int(user_id)
        link_id = hashlib.md5(link.encode()).hexdigest()

        data = clicks.find_one(
            {"user_id": user_id, "link_id": link_id},
            {"_id": 0, "clicks": 1}
        )
        total_clicks = data["clicks"] if data else 0

        return jsonify({"total_clicks": total_clicks}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 📊 All Stats (for Debug/Admin) ==================== #
@click_app.route("/stats", endpoint="click_counter_stats")
def click_counter_stats():
    try:
        data = list(clicks.find({}, {"_id": 0}))
        data.sort(key=lambda x: -x.get("clicks", 0))
        return jsonify({
            "total_records": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================================================== #
# 🏁 End of File — Each Link Has Independent Click Count
# ================================================================== #
