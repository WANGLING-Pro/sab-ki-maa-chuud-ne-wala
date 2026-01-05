#======================================= Start Code ====================================== #

import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from bot import Bot
from config import OWNER_ID
from helper_func import encode, admin

# --- Helper Function: Message se Details nikalna ---
async def get_msg_details(client, message):
    if message.forward_from_chat:
        return message.forward_from_chat.id, message.forward_from_message_id
    elif message.forward_sender_name:
        return None, None
    elif message.text:
        private_match = re.search(r"https://t.me/c/(\d+)/(\d+)", message.text)
        if private_match:
            return int(f"-100{private_match.group(1)}"), int(private_match.group(2))
        public_match = re.search(r"https://t.me/([\w_]+)/(\d+)", message.text)
        if public_match:
            username = public_match.group(1)
            msg_id = int(public_match.group(2))
            try:
                chat = await client.get_chat(username)
                return chat.id, msg_id
            except: return None, None
    return None, None

# --- BATCH COMMAND (Dynamic) ---
@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_msg_ask = await client.ask(text="<b>Forward the First Message</b> from your Batch Channel..", chat_id=message.from_user.id, timeout=60)
        except: return
        channel_id, first_id = await get_msg_details(client, first_msg_ask)
        if channel_id and first_id:
            try:
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
            except Exception as e:
                await message.reply_text(f"❌ **Error - Telegram says:**\n`{e}`\n\nBot ko channel me Admin banayein.")
                return
            break
        else:
            await first_msg_ask.reply("❌ Error: Channel detect nahi hua.")

    while True:
        try:
            second_msg_ask = await client.ask(text=f"<b>Forward the Last Message</b> from: <code>{channel_name}</code>", chat_id=message.from_user.id, timeout=60)
        except: return
        channel_id_2, last_id = await get_msg_details(client, second_msg_ask)
        if channel_id == channel_id_2: break
        await second_msg_ask.reply("❌ Error: Same channel se bhejein.")

    string = f"batch-{channel_id}-{first_id}-{last_id}"
    link = f"https://t.me/{client.username}?start={await encode(string)}"
    await message.reply_text(f"✅ <b>Batch Link Created!</b>\n\n📢 <b>Channel:</b> {channel_name}\n🔗 <b>Link:</b>\n<code>{link}</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]))

# --- SINGLE LINK GENERATOR ---
@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            msg_ask = await client.ask(text="<b>Forward Message</b> or send Link..", chat_id=message.from_user.id, timeout=60)
        except: return
        channel_id, msg_id = await get_msg_details(client, msg_ask)
        if channel_id and msg_id:
            try:
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
            except Exception as e:
                await message.reply_text(f"❌ Error: `{e}`")
                return
            break
        else: await msg_ask.reply("❌ Error detect nahi hua.")

    string = f"get-{channel_id}-{msg_id}"
    link = f"https://t.me/{client.username}?start={await encode(string)}"
    await message.reply_text(f"✅ <b>Link Generated!</b>\n\n📢 <b>Channel:</b> {channel_name}\n🔗 <b>Link:</b>\n<code>{link}</code>")

# --- CUSTOM BATCH (As per your request - Old Logic) ---
@Bot.on_message(filters.private & admin & filters.command("custom_batch"))
async def custom_batch(client: Client, message: Message):
    collected = []
    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)
    await message.reply("Send messages one by one.\nPress **STOP** when you are finished.", reply_markup=STOP_KEYBOARD)

    while True:
        try:
            user_msg = await client.ask(chat_id=message.chat.id, text="Waiting for files...", timeout=300)
        except: break
        if user_msg.text and user_msg.text.strip().upper() == "STOP": break
        try:
            sent = await user_msg.copy(client.db_channel.id)
            collected.append(sent.id)
        except Exception as e:
            await message.reply(f"❌ Failed to copy: {e}")
    
    await message.reply("✅ Custom Batch processing complete.", reply_markup=ReplyKeyboardRemove())
    if collected:
        # Multiplication logic for compatibility with start.py
        start_id = collected[0] * abs(client.db_channel.id)
        end_id = collected[-1] * abs(client.db_channel.id)
        string = f"get-{start_id}-{end_id}"
        link = f"https://t.me/{client.username}?start={await encode(string)}"
        await message.reply(f"🔗 **Custom Batch Link:**\n<code>{link}</code>")

# --- REPLY TO GET LINK ---
@Bot.on_message(filters.command(["getlink", "get"]) & filters.private)
async def getlink_handler(client, message):
    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to any message.")
    msg_id = message.reply_to_message.id
    if message.reply_to_message.forward_from_chat:
        string = f"get-{message.reply_to_message.forward_from_chat.id}-{msg_id}"
    else:
        string = f"get-{client.db_channel.id}-{msg_id}"
    link = f"https://t.me/{client.username}?start={await encode(string)}"
    await message.reply_text(f"✅ **Link Created!**\n<code>{link}</code>")

    #================================================== End Code ===============================================================#
