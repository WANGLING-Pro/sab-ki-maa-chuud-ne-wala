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

async def short_url(client: Client, message: Message, base64_string):
    try:
        # Fix: client.username safe handle
        username = client.me.username if client.me.username else "botusername"
        prem_link = f"https://t.me/{username}?start=yu3elk{base64_string}7"
        short_link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, prem_link)

        buttons = [
            [
                InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", url=short_link),
                InlineKeyboardButton(text="ᴛᴜᴛᴏʀɪᴀʟ", url=TUT_VID)
            ],
            [
                InlineKeyboardButton(text="ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
            ]
        ]

        await message.reply_photo(
            photo=SHORTENER_PIC,
            caption=SHORT_MSG.format(),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except IndexError:
        pass
    except Exception as e:
        print(f"SHORT_URL ERROR = {e}")


@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    id = message.from_user.id
    
    # ✅ PEHLE CHECK - Line 18-19 ka pattern exactly
    is_premium = await is_premium_user(id)

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ You are Banned from using this bot.</b>\n\n"
            "<i>Contact support if you think this is a mistake.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    # ✅ Check Force Subscription
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # File auto-delete time in seconds
    FILE_AUTO_DELETE = await db.get_del_timer()

    # Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Handle normal message flow
    text = message.text

    if len(text) > 7:
        try:
            basic = text.split(" ", 1)[1]
            
            # ✅ YE PART PEHLA WORKING PATTERN
            if basic.startswith("yu3elk"):
                base64_string = basic[6:-1]
            else:
                base64_string = basic

            # ✅ Shortener check - is_premium already checked line 6
            if not is_premium and user_id != OWNER_ID and not basic.startswith("yu3elk"):
                await short_url(client, message, base64_string)
                return

            # Decode
            string = await decode(base64_string)
            argument = string.split("-")

            ids = []
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                    ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
                except Exception as e:
                    print(f"Error decoding IDs: {e}")
                    return

            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except Exception as e:
                    print(f"Error decoding ID: {e}")
                    return

            temp_msg = await message.reply("<b>Please wait...</b>")
            try:
                messages = await get_messages(client, ids)
            except Exception as e:
                await message.reply_text("Something went wrong!")
                print(f"Error getting messages: {e}")
                return
            finally:
                await temp_msg.delete()

            codeflix_msgs = []

            for msg in messages:
                original_caption = msg.caption.html if msg.caption else ""
                caption = f"{original_caption}\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else original_caption
                reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

                try:
                    snt_msg = await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    await asyncio.sleep(0.5)
                    codeflix_msgs.append(snt_msg)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    copied_msg = await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    codeflix_msgs.append(copied_msg)
                except:
                    pass

            if FILE_AUTO_DELETE > 0:
                notification_msg = await message.reply(
                    f"<b>This File will be Deleted in {get_exp_time(FILE_AUTO_DELETE)}. Please save or forward it to your saved messages before it gets Deleted.</b>"
                )

                await asyncio.sleep(FILE_AUTO_DELETE)

                for snt_msg in codeflix_msgs:    
                    if snt_msg:
                        try:    
                            await snt_msg.delete()  
                        except Exception as e:
                            print(f"Error deleting message {snt_msg.id}: {e}")

                try:
                    reload_url = (
                        f"https://t.me/{client.username}?start={message.command[1]}"
                        if message.command and len(message.command) > 1
                        else None
                    )
                    keyboard = InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Get File Again!", url=reload_url)]]
                    ) if reload_url else None

                    await notification_msg.edit(
                        "<b>Your video/file is successfully deleted !!\n\nClick below button to get your deleted video/file 👇</b>",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    print(f"Error updating notification with 'Get File Again' button: {e}")
        
        except Exception as e:
            print(f"Error processing start payload: {e}")
            return

    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• more channels •", url="https://t.me/P_World_81")],
                [
                    InlineKeyboardButton("• about", callback_data="about"),
                    InlineKeyboardButton('help •', callback_data="help")
                ]
            ]
        )
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            message_effect_id=5104841245755180586)
        
        return

   # ================= PAYLOAD =================
ids = None  # Initialize karo
base64_string = None

try:
    payload = message.command[1]
    print(f"PAYLOAD RECEIVED = {payload}")

    is_premium = await is_premium_user(user_id)

    # Normal user check - shortener mode trigger
    if not is_premium and user_id != OWNER_ID and not payload.startswith("yu3elk"):
        print(f"SHORTENER MODE TRIGGERED FOR USER {user_id}")
        await short_url(client, message, payload)
        return

    # Shortener bypass payload extraction
    if payload.startswith("yu3elk"):
        print("Shortener format detected")
        base64_string = payload[6:-1]  # 'yu3elk' aur '7' remove
    else:
        print("Normal payload format")
        base64_string = payload

    print(f"BASE64 STRING TO DECODE = {base64_string}")
    
    # Decode to get IDs
    ids = await decode(base64_string)
    print(f"DECODE SUCCESS - IDS = {ids}, TYPE = {type(ids)}")

except IndexError as ie:
    print(f"INDEX ERROR = {ie}")
    return await message.reply("❌ Invalid Command Format / No payload provided")
    
except Exception as e:
    print(f"PAYLOAD ERROR = {e}")
    import traceback
    print(f"FULL TRACEBACK: {traceback.format_exc()}")
    return await message.reply(f"❌ Invalid Link or Format Error: {str(e)[:100]}")

# Safety check kaafi important hai
if ids is None:
    print("IDS IS NONE - RETURNING")
    return await message.reply("❌ Failed to decode payload - IDs are empty")

# ================= FETCH MESSAGES =================

temp = await message.reply("⏳ Processing your request, please wait...")
msgs = []

try:
    print(f"FETCH ATTEMPT - IDS: {ids}, TYPE: {type(ids)}, CHANNEL_ID: {CHANNEL_ID}")
    
    # Handle different ID types
    if isinstance(ids, list):
        print(f"IDS is list with {len(ids)} items")
        msgs = await client.get_messages(chat_id=CHANNEL_ID, message_ids=ids)
        
    elif isinstance(ids, int):
        print(f"IDS is int: {ids}")
        single_msg = await client.get_messages(chat_id=CHANNEL_ID, message_ids=ids)
        msgs = [single_msg] if single_msg else []
        
    elif isinstance(ids, str):
        print(f"IDS is string: {ids}")
        if ids.isdigit():
            single_msg = await client.get_messages(chat_id=CHANNEL_ID, message_ids=int(ids))
            msgs = [single_msg] if single_msg else []
        else:
            print(f"String IDS not digit format")
            msgs = []
    else:
        print(f"UNKNOWN IDS TYPE: {type(ids)}")
        msgs = []

    print(f"MESSAGES FETCHED = {len(msgs) if isinstance(msgs, list) else 'not a list'}")
    
    # Validate messages
    if not msgs or (isinstance(msgs, list) and all(msg is None for msg in msgs)):
        print("NO VALID MESSAGES FOUND - msgs is empty or all None")
        try:
            await temp.delete()
        except:
            pass
        return await message.reply("❌ File not found in Database (No messages fetched)")

except Exception as fetch_err:
    print(f"FETCH ERROR = {fetch_err}")
    import traceback
    print(f"FETCH ERROR TRACEBACK: {traceback.format_exc()}")
    try:
        await temp.delete()
    except:
        pass
    return await message.reply(f"❌ File not found in Database\n\nError Details: {str(fetch_err)[:80]}")

finally:
    # Temp message delete
    try:
        await temp.delete()
    except:
        pass

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
