import motor.motor_asyncio
from config import DB_URI, DB_NAME
from pytz import timezone
from datetime import datetime, timedelta

# DB
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
premium_db = client[DB_NAME]
collection = premium_db["premium_users"]
IST = timezone("Asia/Kolkata")


# -------------------------
# Helper
# -------------------------
def get_now():
    return datetime.now(IST)


def get_remaining(expiry: datetime):
    return expiry - get_now()


# -------------------------
# Core
# -------------------------
async def is_premium_user(user_id: int) -> bool:
    user = await collection.find_one({"user_id": user_id})
    if not user:
        return False

    expiry = user["expires_at"]
    return get_remaining(expiry).total_seconds() > 0


async def remove_premium(user_id: int):
    await collection.delete_one({"user_id": user_id})


async def add_premium(user_id: int, time_value: int, time_unit: str):
    now = get_now()

    unit = time_unit.lower()
    if unit == "s":
        expires = now + timedelta(seconds=time_value)
    elif unit == "m":
        expires = now + timedelta(minutes=time_value)
    elif unit == "h":
        expires = now + timedelta(hours=time_value)
    elif unit == "d":
        expires = now + timedelta(days=time_value)
    elif unit == "y":
        expires = now + timedelta(days=365 * time_value)
    else:
        raise ValueError("Invalid time unit")

    await collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "expires_at": expires}},
        upsert=True
    )

    return expires.strftime("%Y-%m-%d %H:%M:%S %p IST")


async def remove_expired_users():
    now = get_now()
    await collection.delete_many({"expires_at": {"$lte": now}})


async def list_premium_users():
    users = []
    async for user in collection.find({}):
        remaining = get_remaining(user["expires_at"])
        if remaining.total_seconds() <= 0:
            continue

        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds // 60) % 60
        seconds = remaining.seconds % 60

        expiry_str = user["expires_at"].strftime("%Y-%m-%d %H:%M:%S %p IST")

        users.append(
            f"UserID: {user['user_id']} - {days}d {hours}h {minutes}m {seconds}s left (Expires: {expiry_str})"
        )

    return users


async def check_user_plan(user_id: int):
    user = await collection.find_one({"user_id": user_id})
    if not user:
        return "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ...🥲"

    remaining = get_remaining(user["expires_at"])
    if remaining.total_seconds() <= 0:
        return "ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ʜᴀs ᴇxᴘɪʀᴇᴅ...😣"

    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds // 60) % 60
    seconds = remaining.seconds % 60

    return f"ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ɪs ᴀᴄᴛɪᴠᴇ...🥵 {days}d {hours}h {minutes}m {seconds}s left."
