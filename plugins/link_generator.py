from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pyrogram.errors import FloodWait
from bot import Bot
import asyncio
from helper_func import encode, admin

# ============================================================================================#
# ✅ /batch — Any Channel Batch (Bot must be admin)
# ============================================================================================#

@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):

    # Step 1: Ask first message
    while True:
        try:
            first_message = await client.ask(
                chat_id=message.from_user.id,
                text=(
    "<blockquote>"
    "ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ʙᴀᴛᴄʜ ғɪʀsᴛ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ʏᴏᴜʀ ʙᴀᴛᴄʜ ᴄʜᴀɴɴᴇʟ (𝑤𝑖𝑡ℎ 𝑓𝑜𝑟𝑤𝑎𝑟𝑑 𝑡𝑎𝑔) "
    "Oʀ ɢɪᴠᴇ ᴍᴇ ʙᴀᴛᴄʜ ғɪʀsᴛ ᴍᴇssᴀɢᴇ ʟɪɴᴋ...\n\n"
    ".ᴏʀ ʜᴀᴀ ᴊᴀʟᴅɪ ᴅᴇ sᴀᴍᴊᴀ."
    "</blockquote>"
                ),
                timeout=60
            )
        except:
            return

        if not first_message.forward_from_chat:
            await first_message.reply("ʙᴀᴛᴄʜ ᴄʜᴀɴɴᴇʟ ᴋɪ ᴘᴏsᴛ ᴅᴇ ʙᴇ.")
            continue

        source_chat_id = first_message.forward_from_chat.id
        f_msg_id = first_message.forward_from_message_id
        break

    # Step 2: Ask last message
    while True:
        try:
            second_message = await client.ask(
                chat_id=message.from_user.id,
                text=(
                    "<blockquote>"
                    "ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ʙᴀᴛᴄʜ ʟᴀsᴛ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ʏᴏᴜʀ ʙᴀᴛᴄʜ ᴄʜᴀɴɴᴇʟ (𝑤𝑖𝑡ℎ 𝑓𝑜𝑟𝑤𝑎𝑟𝑑 𝑡𝑎𝑔) Oʀ ɢɪᴠᴇ ᴍᴇ ʙᴀᴛᴄʜ ʟᴀsᴛ ᴍᴇssᴀɢᴇ ʟɪɴᴋ ғʀᴏᴍ ʏᴏᴜʀ ʙᴀᴛᴄʜ ᴄʜᴀɴɴᴇʟ....ᴏʀ ʜᴀᴀ ᴊᴀʟᴅɪ ᴅᴇ sᴀᴍᴊᴀ."
                    "</blockquote>"
                ),
                timeout=60
            )
        except:
            return

        if not second_message.forward_from_chat:
            await second_message.reply("ʀᴇᴀʟ ᴄʜᴀɴɴᴇʟ ᴋɪ ᴘᴏsᴛ ᴅᴇ ʙᴇ.")
            continue

        if second_message.forward_from_chat.id != source_chat_id:
            await second_message.reply("ʙᴏᴛʜ ᴍᴇssᴀɢᴇs ᴍᴜsᴛ ʙᴇ ғʀᴏᴍ sᴀᴍᴇ ᴄʜᴀɴɴᴇʟ.")
            continue

        s_msg_id = second_message.forward_from_message_id
        break

    # Step 3: Check bot is admin in that channel
    try:
        member = await client.get_chat_member(source_chat_id, "me")
        if not member.privileges:
            return await message.reply("ʙᴏᴛ ᴋᴏ ᴀᴅᴍɪɴ ᴛᴏ ʙᴀᴀɴ ᴅᴇ ᴘᴇʜʟᴇ ᴄʜᴜᴛɪʏᴀ.")
    except:
        return await message.reply("ʙᴏᴛ ᴋᴏ ᴀᴅᴍɪɴ ᴛᴏ ʙᴀᴀɴ ᴅᴇ ᴘᴇʜʟᴇ ᴄʜᴜᴛɪʏᴀ.")

    # Step 4: Copy messages to DB
    status = await message.reply("⏳ ᴍᴇssᴀɢᴇs ᴄᴏᴘʏ ʜᴏ ʀᴀʜᴀ ʜᴀɪ ᴡᴀɪᴛ ᴋᴀʀ ʙᴇ...")

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

            await asyncio.sleep(0.3)

        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue

    # ✅ DELETE ONLY STATUS MESSAGE
    try:
        await status.delete()
    except:
        pass

    if not new_ids:
        return await message.reply("❌ ᴋᴏɪ ᴍᴇssᴀɢᴇs ᴄᴏᴘʏ ɴʜɪ ʜᴜᴀ ᴀʙ ɢᴀɴᴅ ᴅᴇ ᴄʜᴀᴀʟ...")

    # Step 5: Generate link
    db_id = abs(client.db_channel.id)
    start_id = new_ids[0] * db_id
    end_id = new_ids[-1] * db_id

    string = f"get-{start_id}-{end_id}"
    base64_string = await encode(string)

    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )

    await message.reply(f"Here is your link:-\n\n{link}", reply_markup=reply_markup)

    # Attach button to last DB message
    try:
        await client.edit_message_reply_markup(
            chat_id=client.db_channel.id,
            message_id=new_ids[-1],
            reply_markup=reply_markup
        )
    except:
        pass


# ============================================================================================#
# ✅ /custom_batch
# ============================================================================================#

@Bot.on_message(filters.private & admin & filters.command("custom_batch"))
async def custom_batch(client: Client, message: Message):
    collected = []
    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)

    await message.reply(
        "Send all messages you want to include in batch.\n\nPress STOP when you're done.",
        reply_markup=STOP_KEYBOARD
    )

    while True:
        try:
            user_msg = await client.ask(
                chat_id=message.chat.id,
                text="ᴡᴀɪᴛ ᴋᴀʀ ʀᴀʜᴇ ʜᴀɪ ғɪʟᴇs/ᴍᴇssᴀɢᴇs...\nᴘʀᴇss sᴛᴏᴘ ᴀɢᴀʀ ᴛᴜᴍʀᴀ ᴍᴀᴀʟ ɴɪᴋᴀʟ ɢᴀʏᴀ ᴛᴏ.",
                timeout=60
            )
        except asyncio.TimeoutError:
            break

        if user_msg.text and user_msg.text.strip().upper() == "STOP":
            break

        try:
            sent = await user_msg.copy(client.db_channel.id, disable_notification=True)
            collected.append(sent.id)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue

    await message.reply("✅ ʙᴀᴛᴄʜ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇ ᴄʜᴀʟ ᴀʙ ɢᴀɴᴅ ᴅᴇ.", reply_markup=ReplyKeyboardRemove())

    if not collected:
        return await message.reply("❌ ᴇᴋᴀ ʙʜɪ ᴍᴇssᴀɢᴇs ʙᴀᴛᴄʜ ᴍᴇ ɴʜɪ ᴅᴀᴀʟ ᴘᴀʏᴀ ᴍᴇ.")

    start_id = collected[0] * abs(client.db_channel.id)
    end_id = collected[-1] * abs(client.db_channel.id)

    string = f"get-{start_id}-{end_id}"
    base64_string = await encode(string)

    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    await message.reply(f"<b>Here is your link:-</b>\n\n{link}", reply_markup=reply_markup)


# ============================================================================================#
# ✅ /getlink
# ============================================================================================#

@Bot.on_message(filters.command(["getlink", "get"]) & filters.private)
async def getlink_handler(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to ANY message to generate link.")

    msg = message.reply_to_message
    msg_id = msg.id

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"

    await message.reply(f"Here is your link:-\n\n{link}")
