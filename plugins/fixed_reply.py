# ================================================================== ##
# ✅ FINAL FIX — Sirf normal users ko fixed reply milega
# ================================================================== ##

from pyrogram import filters
from pyrogram.types import Message
from bot import Bot
from database.database import db
from config import OWNER_ID


async def is_admin_or_owner(uid: int) -> bool:
    """Check karo agar user owner ya admin hai."""
    # Pehle owner check
    if uid == OWNER_ID:
        return True
    # Admin check
    try:
        admins = await db.get_all_admins()  # /add_admin se fetch
        return admins and uid in admins
    except Exception:
        return False  # DB fail → consider normal user


@Bot.on_message(
    filters.private
    & filters.create(lambda _, __, m: True),  # sab private messages
    group=100  # Group high → commands pehle execute, fixed reply last
)
async def fixed_reply_user_only(client, message: Message):
    uid = message.from_user.id

    # --- Admin/Owner check FIRST ---
    if await is_admin_or_owner(uid):
        return  # Admin/owner → fixed reply mat bhejo

    # --- Banned user check ---
    try:
        banned_users = await db.get_ban_users()
        if uid in banned_users:
            return await message.reply_text("⛔️ You are banned. Contact support.")
    except Exception:
        pass

    # --- Command ignore for normal users ---
    if message.text and message.text.startswith("/"):
        return  # Commands ke liye fixed reply mat bhejo

    # --- Normal user fixed reply ---
    try:
        await message.reply_text(
            "<b><blockquote>♲︎︎︎ Pᴏᴡᴇʀᴇᴅ Bʏ : @P_world_81🔞</blockquote></b>"
        )
    except Exception as e:
        print(f"Fixed reply error: {e}")

# ----------------------- End of Fixed reply ----------------------- #

# ================================================================== #
# ____________ more new features will come in Future _______________ #
# ================================================================== #
