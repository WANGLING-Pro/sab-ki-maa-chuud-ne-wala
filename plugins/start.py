# ================= IMPORTS ================= #

import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import *
from database.database import db
from database.db_premium import *

# ================= START COMMAND =================
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id

    # ================= BAN CHECK =================
    banned = await db.banned.find_one({"_id": user_id})
    if banned:
        return await message.reply_text(
            "<b>⛔️ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.</b>\n\n"
            "<i>ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ ɪғ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ", url=BAN_SUPPORT)]]
            )
        )

    # ================= FORCE SUB =================
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # ================= ADD USER =================
    user = await db.users.find_one({"_id": user_id})
    if not user:
        try:
            await db.users.insert_one({"_id": user_id})
        except:
            pass

    # ================= NORMAL START =================
    if len(message.command) == 1:
        return await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=(
                    None if not message.from_user.username
                    else '@' + message.from_user.username
                ),
                mention=message.from_user.mention,
                id=user_id
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴍᴏʀᴇ ᴄʜᴀɴɴᴇʟ •", url="https://t.me/P_World_81")],
                [
                    InlineKeyboardButton("•ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("ʜᴇʟᴘ•", callback_data="help")
                ]
            ]),
            message_effect_id=MSG_EFFECT
        )

    # ================= PAYLOAD =================
    try:
        payload = message.command[1]
        decoded = await decode(payload)
        args = decoded.split("-")

        ids = []

        if len(args) == 3:
            start = int(int(args[1]) / abs(client.db_channel.id))
            end = int(int(args[2]) / abs(client.db_channel.id))
            step = 1 if start <= end else -1
            ids = list(range(start, end + step, step))

        elif len(args) == 2:
            ids = [int(int(args[1]) / abs(client.db_channel.id))]

        else:
            return await message.reply("❌ Invalid link")

    except:
        return await message.reply("❌ Invalid link")

    # ================= FETCH =================
    temp = await message.reply("Please wait...")

    try:
        msgs = await get_messages(client, ids)
    except:
        await temp.delete()
        return await message.reply("❌ File not found")
    finally:
        try:
            await temp.delete()
        except:
            pass

    sent_msgs = []

    # ================= SEND FILES =================
    for msg in msgs:
        if not msg or msg.empty:
            continue

        try:
            s = await msg.copy(
                chat_id=user_id,
                caption=msg.caption.html if msg.caption else None,
                parse_mode=ParseMode.HTML,
                protect_content=PROTECT_CONTENT
            )
            sent_msgs.append(s)
            await asyncio.sleep(0.4)

        except FloodWait as e:
            await asyncio.sleep(e.x)

        except:
            continue

    # ================= AUTO DELETE =================
    FILE_DEL = await db.get_del_timer()

    if FILE_DEL and FILE_DEL > 0 and sent_msgs:

        note = await message.reply(
            f"File will be deleted in {get_exp_time(FILE_DEL)}"
        )

        await asyncio.sleep(FILE_DEL)

        for s in sent_msgs:
            try:
                await s.delete()
            except:
                pass

        try:
            await note.edit("File deleted.")
        except:
            pass


# ================= FORCE SUB =================
async def not_joined(client: Client, message: Message):

    user_id = message.from_user.id
    channels = await db.show_channels()

    buttons = []

    for ch in channels:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member:
                continue
        except:
            pass

        chat = await client.get_chat(ch)

        link = (
            f"https://t.me/{chat.username}"
            if chat.username else await client.export_chat_invite_link(ch)
        )

        buttons.append([
            InlineKeyboardButton(f"ᴊᴏɪɴ {chat.title}", url=link)
        ])

    buttons.append([
        InlineKeyboardButton("ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{client.username}")
    ])

    return await message.reply_photo(
        photo=FORCE_PIC,
        caption="Join all channels first.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
                
    

#•••••••••••••••••••••••••••••••••••••••••••••••••••• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •••••••••••••••••••••••••••••••••••••••••#
from datetime import datetime, timedelta
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

chat_data_cache = {}

async def not_joined(client: Client, message: Message):

    uid = message.from_user.id

    # Payload for Try Again button
    payload = None
    if message.command and len(message.command) > 1:
        payload = message.command[1]

    temp = await message.reply("<b><i>ᴄʜᴇᴄᴋɪɴɢ sᴜʙsᴄʀɪᴘᴛɪᴏɴ...</i></b>")

    buttons = []

    try:
        channels = await db.show_channels()

        for chat_id in channels:
            # Check membership
            try:
                member = await client.get_chat_member(chat_id, uid)
                if member.status in (
                    ChatMemberStatus.MEMBER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER
                ):
                    continue
            except:
                pass

            # Cache chat
            if chat_id not in chat_data_cache:
                chat_data_cache[chat_id] = await client.get_chat(chat_id)

            chat = chat_data_cache[chat_id]
            mode = await db.get_channel_mode(chat_id)

            # Generate link
            if chat.username:
                link = f"https://t.me/{chat.username}"
            else:
                if mode == "on":
                    invite = await client.create_chat_invite_link(
                        chat_id=chat_id,
                        creates_join_request=True,
                        expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                    )
                else:
                    invite = await client.create_chat_invite_link(
                        chat_id=chat_id,
                        expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                    )
                link = invite.invite_link

            buttons.append([
                InlineKeyboardButton(text=f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {chat.title}", url=link)
            ])

        # Try again button
        if payload:
            retry_url = f"https://t.me/{client.username}?start={payload}"
        else:
            retry_url = f"https://t.me/{client.username}"

        buttons.append([
            InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ", url=retry_url)
        ])

        await temp.delete()

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=(
                "<blockquote expandable>"
                "ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴀᴄᴄᴇss ᴛʜɪs ғɪʟᴇ.\n\n"
                "ᴊᴏɪɴ ᴀʟʟ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ \"Try Again\"."
                "</blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            message_effect_id=MSG_EFFECT
        )

    except Exception as e:
        print("FSUB ERROR:", e)

        # Owner ko notify kar
        try:
            await client.send_message(
                OWNER_ID,
                f"⚠️ FSUB ERROR:\n<code>{e}</code>"
            )
        except:
            pass

        try:
            await temp.edit(
                f"<blockquote expandable><b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @I_am_nerev_die</i></b></blockquote>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
            )
        except:
            pass



# =================================================================== #
# 🔥 Premium + Commands + Count (UNCHANGED)
# =================================================================== #

@Bot.on_message(filters.command('myplan') & filters.private)
async def check_plan_cmd(client, message):
    user_id = message.from_user.id
    status = await check_user_plan(user_id)
    await message.reply(status)


@Bot.on_message(filters.command('addpremium') & filters.private & admin)
async def add_premium_user_command(client, msg):
    if len(msg.command) != 4:
        return await msg.reply(
            "Usage: /addpremium <user_id> <value> <unit>\nUnits: s/m/h/d/y"
        )

    try:
        user_id = int(msg.command[1])
        value = int(msg.command[2])
        unit = msg.command[3].lower()

        expires = await add_premium(user_id, value, unit)

        await msg.reply(f"Added premium for {user_id}\nExpires: {expires}")

        await client.send_message(
            user_id,
            f"🎉 Premium Activated!\nDuration: {value}{unit}\nExpires: {expires}"
        )

    except Exception as e:
        await msg.reply(str(e))


@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def remove_premium_cmd(client, msg):
    if len(msg.command) != 2:
        return await msg.reply("Usage: /remove_premium user_id")
    try:
        user = int(msg.command[1])
        await remove_premium(user)
        await msg.reply("Removed.")
    except:
        await msg.reply("Invalid ID")


@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium(client, message):

    ist = timezone("Asia/Kolkata")
    users = collection.find({})
    final = ["Active Premium Users:\n"]

    now = datetime.now(ist)

    async for user in users:
        uid = user["user_id"]
        exp = datetime.fromisoformat(user["expiration_timestamp"]).astimezone(ist)

        remain = exp - now
        if remain.total_seconds() <= 0:
            await collection.delete_one({"user_id": uid})
            continue

        u = await client.get_users(uid)
        d = f"{remain.days}d {remain.seconds//3600}h {(remain.seconds//60)%60}m"

        final.append(
            f"ID: <code>{uid}</code>\nUser: @{u.username}\nName:{u.mention}\nLeft: {d}\n"
        )

    await message.reply("\n".join(final), parse_mode=None)


@Bot.on_message(filters.command("count") & filters.private & admin)
async def count_cmd(client, message):
    c = await db.get_total_verify_count()
    await message.reply(f"Total Verified Tokens Today: <b>{c}</b>")


@Bot.on_message(filters.command('commands') & filters.private & admin)
async def admin_cmd(client, message):
    await message.reply(
        text=CMD_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• Close •", callback_data="close")]]),
        quote=True
                        )

#======================================================== The End =============================================================#
