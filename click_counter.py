# ============================================================== #
# ✅ FLASK CLICK COUNTER — Global link-wise unique click counting
# ============================================================== #

from flask import Flask, request, jsonify, redirect
from pymongo import MongoClient
from urllib.parse import unquote
import os, hashlib, requests, time

click_app = Flask(__name__)

# ==================== ⚙️ MongoDB Connection ==================== #
mongo_url = os.getenv("MONGODB_URL")
if not mongo_url:
    raise ValueError("⚠️ Missing MONGODB_URL environment variable!")

mongo = MongoClient(mongo_url)
db = mongo["botdb"]
clicks = db["clicks"]   # collection for link docs

# helper: make link id
def make_link_id(link: str) -> str:
    return hashlib.md5(link.encode()).hexdigest()


# ==================== 🎯 Redirect Endpoint ==================== #
@click_app.route("/redirect")
def redirect_link():
    try:
        user_id = request.args.get("user_id")
        target = request.args.get("link")

        if not target:
            return "Missing parameter: link", 400

        # decode and normalize target
        target = unquote(target).strip()
        link_id = make_link_id(target)

        # --- ignore bot/preview hits (Telegram preview, crawlers, etc.) ---
        user_agent = request.headers.get("User-Agent", "").lower()
        if any(x in user_agent for x in ("telegram", "bot", "preview", "crawler", "curl", "python-requests")):
            return redirect(target, code=302)

        # --- Ensure target reachable (brief HEAD request) ---
        try:
            r = requests.head(target, timeout=5, allow_redirects=True)
            if r.status_code >= 400:
                r2 = requests.get(target, timeout=5)
                if r2.status_code >= 400:
                    return "⚠️ Target not reachable", 502
        except Exception:
            pass  # still redirect even if HEAD fails

        # --- Unique counting (global): per link_id, not per user_id ---
        if user_id:
            clicked_before = clicks.find_one({
                "link_id": link_id,
                "clicked_users": {"$in": [user_id]}
            })
        else:
            clicked_before = None

        if not clicked_before:
            clicks.update_one(
                {"link_id": link_id},
                {
                    "$inc": {"clicks": 1},
                    "$addToSet": {"clicked_users": user_id},
                    "$setOnInsert": {
                        "target": target,
                        "created_at": int(time.time())
                    }
                },
                upsert=True
            )

        # ✅ Safe redirect (no meta refresh)
        return redirect(target, code=302)

    except Exception as e:
        return f"Error: {e}", 500


# ==================== 🩵 Health Check ==================== #
@click_app.route("/", endpoint="click_counter_home")
def click_counter_home():
    return "✅ Click Counter API Active — Global link-wise tracking ready!"


# ==================== 📊 Get Clicks for Specific Link ==================== #
@click_app.route("/get_clicks", endpoint="click_counter_get_clicks")
def click_counter_get_clicks():
    try:
        link = request.args.get("link")
        if not link:
            return jsonify({"error": "link parameter required"}), 400

        link = unquote(link).strip()
        link_id = make_link_id(link)

        doc = clicks.find_one({"link_id": link_id}, {"_id": 0, "clicks": 1, "clicked_users": 1})
        total_clicks = doc.get("clicks", 0) if doc else 0
        unique_users = len(doc.get("clicked_users", [])) if doc else 0

        return jsonify({
            "total_clicks": total_clicks,
            "unique_users": unique_users
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== 📊 All Stats (for Debug/Admin) ==================== #
@click_app.route("/stats", endpoint="click_counter_stats")
def click_counter_stats():
    try:
        data = list(clicks.find({}, {"_id": 0, "link_id": 1, "target": 1, "clicks": 1}))
        data.sort(key=lambda x: -x.get("clicks", 0))
        return jsonify({
            "total_records": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================================================== #
# 🏁 End of File — Global Click Count (shared by all users)
# ================================================================== #
