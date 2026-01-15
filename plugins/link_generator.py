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

    # Step 1: Ask first message
    while True:
        try:
            first_message = await client.ask(
                chat_id=message.from_user.id,
                text="Forward the FIRST message from ANY channel (bot must be admin there).",
                filters=filters.forwarded,
                timeout=60
            )
        except:
            return

        if not first_message.forward_from_chat:
            await first_message.reply("❌ Forward a real channel post.")
            continue

        source_chat_id = first_message.forward_from_chat.id
        f_msg_id = first_message.forward_from_message_id
        break

    # Step 2: Ask last message
    while True:
        try:
            second_message = await client.ask(
                chat_id=message.from_user.id,
                text="Forward the LAST message from SAME channel.",
                filters=filters.forwarded,
                timeout=60
            )
        except:
            return

        if not second_message.forward_from_chat:
            await second_message.reply("❌ Forward a real channel post.")
            continue

        if second_message.forward_from_chat.id != source_chat_id:
            await second_message.reply("❌ Both messages must be from SAME channel.")
            continue

        s_msg_id = second_message.forward_from_message_id
        break

    # Step 3: Check bot is admin in that channel
    try:
        member = await client.get_chat_member(source_chat_id, "me")
        if not member.privileges:
            return await message.reply("❌ Bot is not admin in this channel.")
    except:
        return await message.reply("❌ Bot is not in this channel.")

    # Step 4: Copy messages to DB
    await message.reply("⏳ Copying messages to DB...")

    new_ids = []

    start = min(f_msg_id, s_msg_id)
    end = max(f_msg_id, s_msg_id)

    for i in range(start, end + 1):
        try:
            msg = await client.get_messages(source_chat_id, i)
            if not msg or msg.empty:
                continue

            copied = await msg.copy(client.db_channel.id)
            new_ids.append(copied.id)

        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue

    if not new_ids:
        return await message.reply("❌ No messages could be copied.")

    # Step 5: Generate link from DB IDs
    db_id = abs(client.db_channel.id)
    start_id = new_ids[0] * db_id
    end_id = new_ids[-1] * db_id

    string = f"get-{start_id}-{end_id}"
    base64_string = await encode(string)

    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )

    await message.reply(
        f"✅ Batch link generated:\n\n{link}",
        reply_markup=reply_markup
            )
