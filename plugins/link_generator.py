#======================================= Start Code ====================================== #

import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import OWNER_ID
from helper_func import encode, admin

# --- Helper Function: Message se Channel ID aur Msg ID nikalna ---
async def get_msg_details(client, message):
    # 1. Agar Forwarded Message hai
    if message.forward_from_chat:
        return message.forward_from_chat.id, message.forward_from_message_id
    
    # 2. Agar Sender Name hidden hai (lekin forward hai)
    elif message.forward_sender_name:
        return None, None
        
    # 3. Agar Text Link hai
    elif message.text:
        # Private Channel Link: https://t.me/c/1234567890/100
        private_match = re.search(r"https://t.me/c/(\d+)/(\d+)", message.text)
        if private_match:
            channel_id = int(f"-100{private_match.group(1)}")
            msg_id = int(private_match.group(2))
            return channel_id, msg_id

        # Public Channel Link: https://t.me/username/100
        public_match = re.search(r"https://t.me/([\w_]+)/(\d+)", message.text)
        if public_match:
            username = public_match.group(1)
            msg_id = int(public_match.group(2))
            try:
                chat = await client.get_chat(username)
                return chat.id, msg_id
            except:
                return None, None
    
    return None, None

# --- BATCH COMMAND ---
@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):
    
    # --- Step 1: First Message ---
    while True:
        try:
            first_msg_ask = await client.ask(
                text="<b>Forward the First Message</b> from your Batch Channel..\n\n<i>(Agar forward tag hidden hai, to post ka Link bhejo)</i>",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return

        channel_id, first_id = await get_msg_details(client, first_msg_ask)
        
        if channel_id and first_id:
            # CHECK: Kya Bot wahan Admin hai? (Access Check)
            try:
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
            except Exception as e:
                await message.reply_text(
                    f"❌ **Error - Telegram says:**\n`{e}`\n\n"
                    "**Possible Reasons:**\n"
                    "1. Bot channel mein add nahi hai.\n"
                    "2. Bot ko channel mein **Admin** power nahi mili hai.",
                    quote=True
                )
                return
            break
        else:
            await first_msg_ask.reply("❌ **Error:** Main Channel detect nahi kar paya.\nKripya sahi se **Forward** karein ya **Link** bhejein.", quote=True)
            continue

    # --- Step 2: Last Message ---
    while True:
        try:
            second_msg_ask = await client.ask(
                text=f"<b>Forward the Last Message</b> from: <code>{channel_name}</code>\n\n<i>(Ya Post Link bhejo)</i>",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return

        channel_id_2, last_id = await get_msg_details(client, second_msg_ask)
        
        if not channel_id_2:
            await second_msg_ask.reply("❌ Invalid Message or Link.", quote=True)
            continue

        if channel_id != channel_id_2:
            await second_msg_ask.reply("❌ **Error:** Ye message kisi aur channel ka hai!\nSame channel se bhejo.", quote=True)
            continue
            
        break

    # --- Step 3: Generation & Beautiful Output ---
    # String Format: batch-ChannelID-FirstID-LastID
    string = f"batch-{channel_id}-{first_id}-{last_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    
    await message.reply_text(
        f"✅ <b>Batch Link Created!</b>\n\n"
        f"📢 <b>Channel:</b> {channel_name}\n"
        f"📂 <b>Range:</b> <code>{first_id}</code> - <code>{last_id}</code>\n\n"
        f"🔗 <b>Link:</b>\n<code>{link}</code>",
        quote=True,
        reply_markup=reply_markup
    )

# --- SINGLE LINK GENERATOR (GenLink) ---
@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            msg_ask = await client.ask(
                text="<b>Forward Message</b> from the Channel..\n<i>(Ya Post Link bhejo)</i>",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
            
        channel_id, msg_id = await get_msg_details(client, msg_ask)
        
        if channel_id and msg_id:
            try:
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
            except Exception as e:
                await message.reply_text(f"❌ **Error:** `{e}`\nBot ko Channel me Admin banao!", quote=True)
                return
            break
        else:
            await msg_ask.reply("❌ Error: Message ID detect nahi hui.", quote=True)
            continue

    string = f"get-{channel_id}-{msg_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    
    await message.reply_text(
        f"✅ <b>Link Generated!</b>\n\n"
        f"📢 <b>Channel:</b> {channel_name}\n"
        f"🆔 <b>Msg ID:</b> <code>{msg_id}</code>\n\n"
        f"🔗 <b>Link:</b>\n<code>{link}</code>",
        quote=True,
        reply_markup=reply_markup
    )

# --- REPLY TO GET LINK (Purana Feature - Wapas add kiya) ---
@Bot.on_message(filters.command(["getlink", "get"]) & filters.private)
async def getlink_handler(client, message):
    if not message.reply_to_message:
        return await message.reply("⚠️ <b>Reply to ANY message</b> to generate link.")

    # Note: Private chat messages ke liye fixed DB_CHANNEL use hoga (Legacy support)
    msg = message.reply_to_message
    msg_id = msg.id
    
    # Agar reply kiya hua message forward hai, to koshish karo uska real channel nikalne ki
    if msg.forward_from_chat:
         # Agar forwarded hai to dynamic link banao
        channel_id = msg.forward_from_chat.id
        string = f"get-{channel_id}-{msg_id}"
    else:
        # Agar normal message hai to Default DB Channel use karo
        string = f"get-{client.db_channel.id}-{msg_id}"

    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    
    await message.reply_text(
        f"✅ <b>Link Created!</b>\n\n"
        f"🔗 <b>Link:</b>\n<code>{link}</code>",
        quote=True,
        reply_markup=reply_markup
            )
        
