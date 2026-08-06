import asyncio
import os
import random
import sys
import time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction, ChatMemberStatus, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatMemberUpdated, ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, InviteHashEmpty, ChatAdminRequired, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import *
from database.database import db


# Commands for adding admins by owner
@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def add_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        admin_ids = await db.get_all_admins() or []
        admins = message.text.split()[1:]

        if not admins:
            return await pro.edit(
                "<b>You need to provide user ID(s) to add as admin.</b>\n\n"
                "<b>Usage:</b>\n"
                "<code>/add_admin [user_id]</code> — Add one or more user IDs\n\n"
                "<b>Example:</b>\n"
                "<code>/add_admin 1234567890 9876543210</code>",
                reply_markup=reply_markup
            )

        admin_list = ""
        for user_id in admins:
            try:
                valid_id = int(user_id)
            except ValueError:
                admin_list += f"<blockquote><b>Invalid ID: <code>{user_id}</code></b></blockquote>\n"
                continue

            if valid_id in admin_ids:
                admin_list += f"<blockquote><b>ID <code>{valid_id}</code> already exists.</b></blockquote>\n"
                continue

            await db.add_admin(valid_id)
            admin_list += f"<b><blockquote>(ID: <code>{valid_id}</code>) added.</blockquote></b>\n"

        await pro.edit(f"<b>✅ Admin(s) added successfully:</b>\n\n{admin_list}", reply_markup=reply_markup)

    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


@Bot.on_message(filters.command('deladmin') & filters.private & filters.user(OWNER_ID))
async def delete_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        admin_ids = await db.get_all_admins() or []
        admins = message.text.split()[1:]

        if not admins:
            return await pro.edit(
                "<b>Please provide valid admin ID(s) to remove.</b>\n\n"
                "<b>Usage:</b>\n"
                "<code>/deladmin [user_id]</code> — Remove specific IDs\n"
                "<code>/deladmin all</code> — Remove all admins",
                reply_markup=reply_markup
            )

        if len(admins) == 1 and admins[0].lower() == "all":
            if admin_ids:
                for admin_id in admin_ids:
                    await db.del_admin(admin_id)
                ids = "\n".join(f"<blockquote><code>{admin}</code> ✅</blockquote>" for admin in admin_ids)
                return await pro.edit(f"<b>⛔️ All admin IDs have been removed:</b>\n{ids}", reply_markup=reply_markup)
            else:
                return await pro.edit("<b><blockquote>No admin IDs to remove.</blockquote></b>", reply_markup=reply_markup)

        passed = ""
        for admin_id in admins:
            try:
                valid_id = int(admin_id)
            except ValueError:
                passed += f"<blockquote><b>Invalid ID: <code>{admin_id}</code></b></blockquote>\n"
                continue

            if valid_id in admin_ids:
                await db.del_admin(valid_id)
                passed += f"<blockquote><code>{valid_id}</code> ✅ Removed</blockquote>\n"
            else:
                passed += f"<blockquote><b>ID <code>{valid_id}</code> not found in admin list.</b></blockquote>\n"

        await pro.edit(f"<b>⛔️ Admin removal result:</b>\n\n{passed}", reply_markup=reply_markup)

    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)


@Bot.on_message(filters.command('admins') & filters.private & admin)
async def get_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    try:
        admin_ids = await db.get_all_admins() or []

        if not admin_ids:
            admin_list = "<b><blockquote>❌ No admins found.</blockquote></b>"
        else:
            admin_items = []
            for admin_id in admin_ids:
                try:
                    user = await client.get_users(admin_id)
                    first_name = user.first_name if user.first_name else "Admin"
                    admin_items.append(
                        f"<b><blockquote>👤 <a href='tg://user?id={admin_id}'>{first_name}</a> | ID: <code>{admin_id}</code></blockquote></b>"
                    )
                except Exception:
                    admin_items.append(
                        f"<b><blockquote>👤 <a href='tg://user?id={admin_id}'>Admin</a> | ID: <code>{admin_id}</code></blockquote></b>"
                    )
            admin_list = "\n".join(admin_items)

        await pro.edit(f"<b>⚡ Current Admin List:</b>\n\n{admin_list}", reply_markup=reply_markup)

    except Exception as e:
        await pro.edit(f"<b>❌ Error occurred:</b> <code>{str(e)}</code>", reply_markup=reply_markup)
