# Copyright (C) 2025 by WANGLING-Pro@Github, 
# < https://github.com/WANGLING-Pro > Project,
# This file is part of < https://github.com/WANGLING-Pro/sab-ki-maa-chuud-ne-wala > project,
# and is released under the MIT License.
# Please see < https://github.com/WANGLING-Pro/sab-ki-maa-chuud-ne-wala >
#
# All rights reserved.

from pyrogram import Client, filters
from bot import Bot
from config import *
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import db
from helper_func import admin
import asyncio

# Tracks which admins are currently expected to send shortener URL+API text
pending_shortener_input = {}

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close')]
            ])
        )

    elif data == "start":
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'),
                 InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')]
            ])
        )


# Don't Remove Credit @P_World_18, @I_am_Never_die
# Ask Doubt on telegram @Upcoming
#
# Copyright (C) 2025 by WANGLING-Pro@Github, < https://github.com/WANGLING-Pro >.
#
# This file is part of < https://github.com/WANGLING-Pro/sab-ki-maa-chuud-ne-wala > project,
# and is released under the MIT License.
# Please see < https://github.com/WANGLING-Pro/sab-ki-maa-chuud-ne-wala >
#
# All rights reserved.
#


    elif data == "premium":
        sent_msg = await client.send_photo(
            chat_id=query.message.chat.id,
            photo=QR_PIC,
            caption=(
                f"✨ 𝗘𝘅𝗰𝗹𝘂𝘀𝗶𝘃𝗲 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗠𝗲𝗺𝗯𝗲𝗿𝘀𝗵𝗶𝗽 ✨\n"
                f"<i>sᴛᴇᴘ ɪɴᴛᴏ ᴛʜᴇ 𝖵𝖨𝖯 ᴢᴏɴᴇ</i>\n\n"
                f"🎁 <b>ᴡʜᴀᴛ ʏᴏᴜ ᴜɴʟᴏᴄᴋ:</b>\n"
                f"✔︎ ᴢᴇʀᴏ ᴀᴅs, ᴢᴇʀᴏ ᴡᴀɪᴛɪɴɢ — ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss.\n"
                f"✔︎ ᴘʀɪᴏʀɪᴛʏ ʀᴇᴘʟɪᴇs ᴡʜᴇɴᴇᴠᴇʀ ʏᴏᴜ ɴᴇᴇᴅ ʜᴇʟᴘ.\n"
                f"✔︎ ᴇᴀʀʟʏ ᴀᴄᴄᴇss ᴛᴏ ɴᴇᴡ ᴅʀᴏᴘs & ᴇxᴄʟᴜsɪᴠᴇ  ᴄᴏɴᴛᴇɴᴛ.\n\n"
                f"💌 <b>ᴘɪᴄᴋ ʏᴏᴜʀ ᴘʟᴀɴ:</b>\n\n"
                f"❣︎ 7 ᴅᴀʏs — <b>{PRICE1}</b>\n"
                f"❣︎ 1 ᴍᴏɴᴛʜ — <b>{PRICE2}</b>\n"
                f"❣︎ 3 ᴍᴏɴᴛʜs — <b>{PRICE3}</b>\n"
                f"❣︎ 6 ᴍᴏɴᴛʜs — <b>{PRICE4}</b>\n"
                f"❣︎ 1 ʏᴇᴀʀ — <b>{PRICE5}</b>\n\n"
                f"💸 <b>ʜᴏᴡ ᴛᴏ ᴘᴀʏ:</b>\n"
                f"ᴜᴘɪ ɪᴅ → <code>{UPI_ID}</code>\n"
                f"<i>(ᴛᴀᴘ ᴛᴏ ᴄᴏᴘʏ ɪɴsᴛᴀɴᴛʟʏ)</i>\n\n"
                f"✔︎ ᴘᴀʏ → 📸 sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ → ⚡ ɢᴇᴛ ɪɴsᴛᴀɴᴛ ᴀᴄᴛɪᴠᴀᴛɪᴏɴ.\n\n"
                f"🎯 ᴡᴀɴᴛ ᴀ ᴄᴜsᴛᴏᴍ ᴘʟᴀɴ? ᴊᴜsᴛ ᴘɪɴɢ ᴛʜᴇ ᴀᴅᴍɪɴ ʙᴇʟᴏᴡ.\n\n"
                f"🚨 <i>sᴇᴀᴛs ᴀʀᴇ 𝖫𝖨𝖬𝖨𝖳𝖤𝖣 ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀs – ɢʀᴀʙ ʏᴏᴜʀs ɴᴏᴡ!</i>"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⎯⎯꯭̽ །͠𝛐͢ꪎ᪳̑𝛊𝐜꯭̈⎯꯭̽❥", url=SCREENSHOT_URL),
                        InlineKeyboardButton("• ᴘᴏʀɴ ᴡᴏʀʟᴅ", url=MAIN_CHANNEL_URL)
                    ]
                ]
            )
        )

        async def _auto_delete(msg, delay):
            await asyncio.sleep(delay)
            try:
                await msg.delete()
            except Exception:
                pass

        asyncio.create_task(_auto_delete(sent_msg, 120))


    elif data == "shortener_menu":
        if not (query.from_user.id == OWNER_ID or await db.admin_exist(query.from_user.id)):
            return await query.answer("⛔ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ", show_alert=True)

        status = await db.get_shortener_status()
        status_text = "🟢 ᴏɴ" if status == "on" else "🔴 ᴏғғ"
        toggle_text = "🔴 ᴛᴜʀɴ ᴏғғ" if status == "on" else "🟢 ᴛᴜʀɴ ᴏɴ"
        new_status = "off" if status == "on" else "on"

        await query.message.edit_text(
            f"<b>⚙️ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴɢs</b>\n\nCurrent Status: {status_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(toggle_text, callback_data=f"shortener_toggle_{new_status}")],
                [InlineKeyboardButton("🔑 sᴇᴛ ᴀᴘɪ & ᴜʀʟ", callback_data="shortener_setapi")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="start")]
            ])
        )

    elif data.startswith("shortener_toggle_"):
        if not (query.from_user.id == OWNER_ID or await db.admin_exist(query.from_user.id)):
            return await query.answer("⛔ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ", show_alert=True)

        new_status = data.split("_")[-1]
        await db.set_shortener_status(new_status)
        await query.answer(f"sʜᴏʀᴛᴇɴᴇʀ ᴛᴜʀɴᴇᴅ {new_status.upper()}")

        status_text = "🟢 ᴏɴ" if new_status == "on" else "🔴 ᴏғғ"
        toggle_text = "🔴 ᴛᴜʀɴ ᴏғғ" if new_status == "on" else "🟢 ᴛᴜʀɴ ᴏɴ"
        flip_status = "off" if new_status == "on" else "on"

        await query.message.edit_text(
            f"<b>⚙️ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴɢs</b>\n\nCurrent Status: {status_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(toggle_text, callback_data=f"shortener_toggle_{flip_status}")],
                [InlineKeyboardButton("🔑 sᴇᴛ ᴀᴘɪ & ᴜʀʟ", callback_data="shortener_setapi")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="start")]
            ])
        )

    elif data == "shortener_setapi":
        if not (query.from_user.id == OWNER_ID or await db.admin_exist(query.from_user.id)):
            return await query.answer("⛔ Not allowed", show_alert=True)

        pending_shortener_input[query.from_user.id] = True
        await query.message.edit_text(
            "<b>🔑 sᴇɴᴅ ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇʀ ᴜʀʟ ᴀɴᴅ ᴀᴘɪ ᴋᴇʏ ɪɴ ᴏɴᴇ ᴍsssᴀɢᴇ, sᴘᴀᴄᴇ sᴇ sᴇᴘᴀʀᴀᴛᴇ ᴋᴀʀᴋᴇ:</b>\n\n"
            "<code>yourdomain.com your_api_key</code>\n\n"
            "Example:\n<code>adrinolinks.in 8f2b91xyz</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("‹ ᴄᴀɴᴄᴇʟ", callback_data="shortener_menu")]])
        )


    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await db.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "ᴏғғ" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        cid, action = data.split("_")[2:]
        cid = int(cid)
        mode = "on" if action == "on" else "off"

        await db.set_channel_mode(cid, mode)
        await query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        # Refresh the same channel's mode view
        chat = await client.get_chat(cid)
        status = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await query.message.edit_text(
            f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "fsub_back":
        channels = await db.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await db.get_channel_mode(cid)
                status = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except:
                continue

        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# Don't Remove Credit @P_World_18, @I_am_Never_die
# Ask Doubt on telegram @Upcoming
#
# Copyright (C) 2025 by WANGLING-Pro@Github, < https://github.com/WANGLING-Pro >.
#
# This file is part of < https://github.com/WANGLING-Pro/sab-ki-maa-chuud-ne-wala > project,
# and is released under the MIT License.
# Please see < https://github.com/WANGLING-Pro/sab-ki-maa-chuud-ne-wala/new/Shortner >
#
# All rights reserved.
#


@Bot.on_message(filters.private & filters.text & admin, group=1)
async def catch_shortener_input(client, message: Message):
    uid = message.from_user.id
    if not pending_shortener_input.get(uid):
        return

    if message.text.startswith("/"):
        return

    parts = message.text.strip().split(" ", 1)
    if len(parts) != 2:
        return await message.reply("❌ Wrong format. Send like:\n<code>yourdomain.com your_api_key</code>")

    url, api = parts[0].strip(), parts[1].strip()
    await db.set_shortener_config(url, api)
    pending_shortener_input.pop(uid, None)

    await message.reply(
        f"✅ Shortener Config Updated!\n\nURL: <code>{url}</code>\nAPI: <code>{api}</code>"
    )
