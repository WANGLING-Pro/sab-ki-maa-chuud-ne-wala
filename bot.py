from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
import time
import sys
import logging

from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode
from datetime import datetime

from config import *
from database.db_premium import *
from database.database import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler


# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ================= SCHEDULER =================
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

scheduler.add_job(remove_expired_users, "interval", minutes=5)


async def daily_reset_task():
    try:
        await db.reset_all_verify_counts()
    except Exception as e:
        logger.error(f"Reset error: {e}")


scheduler.add_job(daily_reset_task, "cron", hour=0, minute=0)


# ================= BOT CLASS =================
class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )

    async def start(self):
        await super().start()

        if not scheduler.running:
            scheduler.start()

        self.uptime = datetime.now()
        me = await self.get_me()
        self.username = me.username

        # ================= DB CHANNEL CHECK =================
        try:
            self.db_channel = await self.get_chat(CHANNEL_ID)
            test = await self.send_message(self.db_channel.id, "Test")
            await test.delete()
        except Exception as e:
            logger.error(f"DB Channel Error: {e}")
            logger.error("Bot stopped. Check CHANNEL_ID or bot admin status.")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)

        # ================= ASCII + BRAND =================
        logger.info(f"""
⠛⠛⣿⣿⣿⣿⣿⡷⢶⣦⣶⣶⣤⣤⣤⣀⠀⠀⠀
⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀
⠀⠀⠀⠉⠉⠉⠙⠻⣿⣿⠿⠿⠛⠛⠛⠻⣿⣿⣇⠀
⠀⠀⢤⣀⣀⣀⠀⠀⢸⣷⡄⠀⣁⣀⣤⣴⣿⣿⣿⣆
⠀⠀⠀⠀⠹⠏⠀⠀⠀⣿⣧⠀⠹⣿⣿⣿⣿⣿⡿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠿⠇⢀⣼⣿⣿⠛⢯⡿⡟
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠦⠴⢿⢿⣿⡿⠷⠀⣿⠀
⠀⠀⠀⠀⠀⠀⠀⠙⣷⣶⣶⣤⣤⣤⣤⣤⣶⣦⠃⠀
⠀⠀⠀⠀⠀⠀⠀⢐⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿
         ⠙⠻⢿⣿⣿⣿⣿⠟⠁

🚀 Bot Running..! Made by @P_world_81
""")

        logger.info(f"Bot started as @{self.username}")

        # ================= WEB SERVER =================
        try:
            app = web.AppRunner(await web_server())
            await app.setup()

            site = web.TCPSite(app, "0.0.0.0", int(PORT))
            await site.start()

            logger.info(f"Web server running on port {PORT}")
        except Exception as e:
            logger.error(f"Web server failed: {e}")

        # ================= OWNER NOTIFY =================
        try:
            await self.send_message(
                OWNER_ID,
                "<b><blockquote> Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ by @p_world_81🔞</blockquote></b>"
            )
        except Exception:
            pass

    async def stop(self, *args):
        try:
            await super().stop()
        except:
            pass
        logger.info("Bot stopped.")

    def run(self):
        loop = asyncio.get_event_loop()

        while True:
            try:
                loop.run_until_complete(self.start())
                logger.info("Bot is now running. Thanks to @I_am_nerev_die")
                loop.run_forever()
                break

            except FloodWait as e:
                wait_time = int(e.value)
                logger.warning(f"FloodWait detected. Sleeping for {wait_time} seconds...")
                time.sleep(wait_time)

            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break

            except Exception as e:
                logger.error(f"Bot crashed: {e}")
                break

        loop.run_until_complete(self.stop())
