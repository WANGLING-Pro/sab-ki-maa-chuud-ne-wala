import motor.motor_asyncio
from datetime import datetime, timedelta
from config import DB_URI, DB_NAME


class Database:
    def __init__(self, uri, name):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[name]

        # Collections
        self.users = self.db["users"]
        self.admins = self.db["admins"]
        self.banned = self.db["banned_users"]
        self.fsub = self.db["fsub_channels"]
        self.del_timer = self.db["del_timer"]
        self.verify = self.db["verify"]
        self.req_fsub = self.db["request_fsub"]
        self.verify_count = self.db["verify_count"]

    # ===================== USERS =====================

    async def present_user(self, user_id: int):
        return bool(await self.users.find_one({"_id": user_id}))

    async def add_user(self, user_id: int):
        await self.users.update_one(
            {"_id": user_id},
            {"$setOnInsert": {"_id": user_id}},
            upsert=True
        )

    async def del_user(self, user_id: int):
        await self.users.delete_one({"_id": user_id})

    async def full_userbase(self):
        users = await self.users.find({}, {"_id": 1}).to_list(length=None)
        return [u["_id"] for u in users]

    # ===================== ADMINS =====================

    async def admin_exist(self, admin_id: int):
        return bool(await self.admins.find_one({"_id": admin_id}))

    async def add_admin(self, admin_id: int):
        await self.admins.update_one(
            {"_id": admin_id},
            {"$setOnInsert": {"_id": admin_id}},
            upsert=True
        )

    async def del_admin(self, admin_id: int):
        await self.admins.delete_one({"_id": admin_id})

    async def get_all_admins(self):
        data = await self.admins.find({}, {"_id": 1}).to_list(length=None)
        return [x["_id"] for x in data]

    # ===================== BANNED =====================

    async def ban_user_exist(self, user_id: int):
        return bool(await self.banned.find_one({"_id": user_id}))

    async def add_ban_user(self, user_id: int):
        await self.banned.update_one(
            {"_id": user_id},
            {"$setOnInsert": {"_id": user_id}},
            upsert=True
        )

    async def del_ban_user(self, user_id: int):
        await self.banned.delete_one({"_id": user_id})

    async def get_ban_users(self):
        data = await self.banned.find({}, {"_id": 1}).to_list(length=None)
        return [x["_id"] for x in data]

    # ===================== AUTO DELETE TIMER =====================

    async def set_del_timer(self, seconds: int):
        await self.del_timer.update_one(
            {"_id": "timer"},
            {"$set": {"value": int(seconds)}},
            upsert=True
        )

    async def get_del_timer(self):
        data = await self.del_timer.find_one({"_id": "timer"})
        if not data:
            return 0
        return int(data.get("value", 0))

    # ===================== FORCE SUB CHANNELS =====================

    async def add_channel(self, channel_id: int):
        await self.fsub.update_one(
            {"_id": channel_id},
            {"$setOnInsert": {"_id": channel_id, "mode": "off"}},
            upsert=True
        )

    async def rem_channel(self, channel_id: int):
        await self.fsub.delete_one({"_id": channel_id})

    async def show_channels(self):
        data = await self.fsub.find({}, {"_id": 1}).to_list(length=None)
        return [x["_id"] for x in data]

    async def get_channel_mode(self, channel_id: int):
        data = await self.fsub.find_one({"_id": channel_id})
        if not data:
            return "off"
        return data.get("mode", "off")

    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub.update_one(
            {"_id": channel_id},
            {"$set": {"mode": mode}},
            upsert=True
        )

    # ===================== REQUEST FORCE SUB =====================

    async def req_user(self, channel_id: int, user_id: int):
        await self.req_fsub.update_one(
            {"_id": channel_id},
            {"$addToSet": {"users": user_id}},
            upsert=True
        )

    async def del_req_user(self, channel_id: int, user_id: int):
        await self.req_fsub.update_one(
            {"_id": channel_id},
            {"$pull": {"users": user_id}}
        )

    async def req_user_exist(self, channel_id: int, user_id: int):
        data = await self.req_fsub.find_one({"_id": channel_id, "users": user_id})
        return bool(data)

    # ===================== VERIFY SYSTEM =====================

    async def get_verify_status(self, user_id: int):
        data = await self.verify.find_one({"_id": user_id})
        if not data:
            return {
                "is_verified": False,
                "verified_time": 0,
                "verify_token": "",
                "link": ""
            }
        return data

    async def update_verify_status(self, user_id: int, verify_token="", is_verified=False, verified_time=0, link=""):
        await self.verify.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "verify_token": verify_token,
                    "is_verified": is_verified,
                    "verified_time": verified_time,
                    "link": link
                }
            },
            upsert=True
        )

    # ===================== VERIFY COUNT =====================

    async def set_verify_count(self, user_id: int, count: int):
        await self.verify_count.update_one(
            {"_id": user_id},
            {"$set": {"count": int(count)}},
            upsert=True
        )

    async def get_verify_count(self, user_id: int):
        data = await self.verify_count.find_one({"_id": user_id})
        if not data:
            return 0
        return int(data.get("count", 0))

    async def reset_all_verify_counts(self):
        await self.verify_count.update_many({}, {"$set": {"count": 0}})

    async def get_total_verify_count(self):
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$count"}}}
        ]
        result = await self.verify_count.aggregate(pipeline).to_list(length=1)
        if not result:
            return 0
        return result[0]["total"]


# ===================== INIT =====================

db = Database(DB_URI, DB_NAME)
