import motor.motor_asyncio
from config import DB_URI, DB_NAME
from datetime import datetime, timedelta

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
premium_db = client[DB_NAME]
collection = premium_db["premium_users"]


def now():
    return datetime.utcnow()


def get_remaining(expiry):
    if expiry.tzinfo is not None:
        expiry = expiry.replace(tzinfo=None)

    return expiry - now()


async def is_premium_user(user_id: int):
    user = await collection.find_one({"user_id": user_id})

    if not user:
        return False

    expiry = user["expires_at"]

    if expiry.tzinfo is not None:
        expiry = expiry.replace(tzinfo=None)

    return expiry > now()


async def remove_premium(user_id: int):
    await collection.delete_one({"user_id": user_id})


async def add_premium(user_id: int, value: int, unit: str):

    start = now()

    unit = unit.lower()

    if unit == "s":
        expiry = start + timedelta(seconds=value)

    elif unit == "m":
        expiry = start + timedelta(minutes=value)

    elif unit == "h":
        expiry = start + timedelta(hours=value)

    elif unit == "d":
        expiry = start + timedelta(days=value)

    elif unit == "y":
        expiry = start + timedelta(days=value * 365)

    else:
        raise ValueError("Invalid Unit")

    await collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "expires_at": expiry
            }
        },
        upsert=True
    )

    return expiry.strftime("%d-%m-%Y %I:%M:%S %p UTC")


async def remove_expired_users():
    await collection.delete_many(
        {
            "expires_at": {
                "$lte": now()
            }
        }
    )


async def list_premium_users():

    result = []

    async for user in collection.find({}):

        expiry = user["expires_at"]

        if expiry.tzinfo is not None:
            expiry = expiry.replace(tzinfo=None)

        remaining = expiry - now()

        if remaining.total_seconds() <= 0:
            continue

        d = remaining.days
        h = remaining.seconds // 3600
        m = (remaining.seconds // 60) % 60
        s = remaining.seconds % 60

        result.append(
            f"UserID : {user['user_id']}\n"
            f"Remaining : {d}d {h}h {m}m {s}s\n"
            f"Expires : {expiry}\n"
        )

    return result


async def check_user_plan(user_id: int):

    user = await collection.find_one({"user_id": user_id})

    if not user:
        return "❌ You don't have Premium."

    expiry = user["expires_at"]

    if expiry.tzinfo is not None:
        expiry = expiry.replace(tzinfo=None)

    remaining = expiry - now()

    if remaining.total_seconds() <= 0:
        return "❌ Premium Expired."

    d = remaining.days
    h = remaining.seconds // 3600
    m = (remaining.seconds // 60) % 60
    s = remaining.seconds % 60

    return f"ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ɪs ᴀᴄᴛɪᴠᴇ...🥵 {days}d {hours}h {minutes}m {seconds}s left."