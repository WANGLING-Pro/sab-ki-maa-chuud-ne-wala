# ============================================================== #
# ✅ FLASK CLICK COUNTER — Redirect pe MongoDB clicks update
# ============================================================== #

from flask import Flask, request, redirect
from pymongo import MongoClient
import os

# ============================================================ #
# 🔧 Flask Application Setup
# ============================================================ #
click_app = Flask(__name__)

# ============================================================ #
# ⚙️ MongoDB Connection Setup
# ============================================================ #
mongo_url = os.getenv("MONGODB_URL")
if not mongo_url:
    raise ValueError("⚠️ MONGODB_URL environment variable not found!")

mongo = MongoClient(mongo_url)
db = mongo["botdb"]
clicks = db["clicks"]

# ============================================================ #
# 🎯 Redirect Endpoint — Track Clicks
# ============================================================ #
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

        # Increment click counter
        clicks.update_one(
            {"user_id": user_id},
            {"$inc": {"clicks": 1}},
            upsert=True
        )

        return f"""
<html>
  <head>
    <meta http-equiv="refresh" content="0; url={target}" />
  </head>
  <body>
    <p>Redirecting...</p>
  </body>
</html>
"""

    except Exception as e:
        return f"Error: {e}", 500


# =================================================================== #
# 🩵 Health Check Route
# =================================================================== #
@click_app.route("/")
def home():
    return "✅ Click Counter API Active — Ready to track user clicks!"


# ================================================================== #
# 🏁 End of File — click Counter. — More New future Coming soon
# ================================================================== #
