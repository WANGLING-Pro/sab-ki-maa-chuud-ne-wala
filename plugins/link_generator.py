from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from bot import Bot
import asyncio
from helper_func import encode, admin

# =========================================================
# ✅ /batch — Any Channel Batch (Bot must be admin)
# =========================================================

@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):

    # ---------- FIRST MESSAGE ----------
    while True:
        try:
            first_message = await client.ask(
                chat_id=message.from_user.id,
                text="Forward the FIRST message from ANY channel (bot must be admin there).",
                filters=filters.forwarded,
                timeout=120
            )
        except:
            return

        if not first_message.forward_from_chat or not first_message.forward_from_message_id:
            await first_message.reply("❌ Forward a channel post, not user message.")
            continue

        chat_id = first_message.forward_from_chat.id
        f_msg_id = first_message.forward_from_message_id

        # ✅ ADMIN CHECK
        try:
            member = await client.get_chat_member(chat_id, "me")
            if not member.privileges:
                await first_message.reply("❌ Bot is not admin in this channel.")
                continue
        except:
            await first_message.reply("❌ Bot is not in this channel.")
            continue

        break

    # ---------- SECOND MESSAGE ----------
    while True:
        try:
            second_message = await client.ask(
                chat_id=message.from_user.id,
                text="Forward the LAST message from SAME channel.",
                filters=filters.forwarded,
                timeout=120
            )
        except:
            return

        if not second_message.forward_from_chat or not second_message.forward_from_message_id:
            await second_message.reply("❌ Forward a channel post.")
            continue

        if second_message.forward_from_chat.id != chat_id:
            await second_message.reply("❌ Both messages must be from SAME channel.")
            continue

        s_msg_id = second_message.forward_from_message_id
        break

    # ---------- BUILD LINK ----------
    string = f"batch-{chat_id}-{f_msg_id}-{s_msg_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )

    await message.reply_text(
        f"<b>✅ Batch link generated:</b>\n\n{link}",
        reply_markup=reply_markup
    )

# =========================================================
# ✅ /genlink — Any Channel Single File
# =========================================================

@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def genlink(client: Client, message: Message):

    while True:
        try:
            channel_message = await client.ask(
                chat_id=message.from_user.id,
                text="Forward a message from ANY channel (bot must be admin).",
                filters=filters.forwarded,
                timeout=120
            )
        except:
            return

        if not channel_message.forward_from_chat or not channel_message.forward_from_message_id:
            await channel_message.reply("❌ Forward a channel post.")
            continue

        chat_id = channel_message.forward_from_chat.id
        msg_id = channel_message.forward_from_message_id

        # ADMIN CHECK
        try:
            member = await client.get_chat_member(chat_id, "me")
            if not member.privileges:
                await channel_message.reply("❌ Bot is not admin in this channel.")
                continue
        except:
            await channel_message.reply("❌ Bot is not in this channel.")
            continue

        break

    string = f"get-{chat_id}-{msg_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )

    await message.reply_text(
        f"<b>✅ File link generated:</b>\n\n{link}",
        reply_markup=reply_markup
        )
