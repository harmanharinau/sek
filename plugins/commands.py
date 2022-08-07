import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, send_more_files, gen_url, broadcast_messages, broadcast_notification
from database.connections_mdb import active_connection
from database.quickdb import remove_inst, get_ids, add_sent_files, get_verification, remove_verification, add_verification, count_sent_files, add_update_msg, remove_update_msg, get_update_msg
from database.tvseriesfilters import add_tvseries_filter, update_tvseries_filter, getlinks, find_tvseries_filter, remove_tvseries
from database.notification import find_notification, remove_notification, update_notification, add_notification, find_allusers
import re
import json
import base64
import time
logger = logging.getLogger(__name__)

BATCH_FILES = {}


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):

    if message.chat.type in ['group', 'supergroup']:
        buttons = [
            [
                InlineKeyboardButton('🤖 Updates', url='https://t.me/TMWAD')
            ],
            [
                InlineKeyboardButton(
                    'ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))
            await db.add_chat(message.chat.id, message.chat.title)
        return
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('➕ Add Me To Your Groups ➕',
                                 url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton(
                '🔍 Search', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖 Updates', url='https://t.me/TMWAD')
        ], [
            InlineKeyboardButton('ℹ️ Help', callback_data='help'),
            InlineKeyboardButton('😊 About', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(
                message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        btn = [
            [
                InlineKeyboardButton(
                    "🤖 Join Updates Channel", url="https://t.me/TMWAD"
                )
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub'
                btn.append([InlineKeyboardButton(
                    " 🔄 Try Again", callback_data=f"{pre}#{file_id}")])
            except IndexError:
                btn.append([InlineKeyboardButton(
                    " 🔄 Try Again", url=f"https://t.me/{temp.U_NAME}/{message.command[1]}")])
            except:
                return

        await client.send_message(
            chat_id=message.from_user.id,
            text="**Please Join My Updates Channel to use this Bot!**",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('➕ Add Me To Your Groups ➕',
                                 url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton(
                '🔍 Search', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖 Updates', url='https://t.me/TMWAD')
        ], [
            InlineKeyboardButton('ℹ️ Help', callback_data='help'),
            InlineKeyboardButton('😊 About', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(
                message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,

        )
        return

    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""

    if data.split("-", 1)[0] == "FEND":
        t = time.time()
        await remove_verification(message.from_user.id)
        file_id = data.split("-", 1)[1]
        await add_verification(message.from_user.id, 'verified', file_id, t)

        tt = time.localtime(t+43200)
        current_time = time.strftime("%D  %H:%M:%S", tt)
        await message.reply(
            text=f"""
                <p>you'r verified Succusfully. access until {current_time}</p>
                """
        )
        idstring = await get_ids(file_id)

        if idstring:
            await remove_inst(file_id)
            idstring = idstring['links']
            fileids = idstring.split("L_I_N_K")
            sendmsglist = []
            for file_id in fileids:
                files_ = await get_file_details(file_id)
                if not files_:
                    try:
                        msg = await client.send_cached_media(
                            chat_id=message.from_user.id,
                            file_id=file_id
                        )
                        filetype = msg.media
                        file = getattr(msg, filetype)
                        title = file.file_name
                        size = get_size(file.file_size)
                        f_caption = f"<code>{title}</code>"
                        if CUSTOM_FILE_CAPTION:
                            try:
                                f_caption = CUSTOM_FILE_CAPTION.format(
                                    file_name='' if title is None else title, file_size='' if size is None else size, file_caption='')
                            except:
                                return
                        await msg.edit_caption(f_caption)
                        return
                    except:
                        pass
                files = files_[0]
                title = files.file_name
                size = get_size(files.file_size)
                f_caption = files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(
                            file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption = f_caption
                if f_caption is None:
                    f_caption = f"{files.file_name}"
                k = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                )
                sendmsglist.append(k)
                await add_sent_files(message.from_user.id, file_id)

                await asyncio.sleep(2)

            await message.reply('𝕋𝕙𝕒𝕟𝕜 𝕐𝕠𝕦 𝔽𝕠𝕣 𝕌𝕤𝕚𝕟𝕘 𝕄𝕖')
            kk = await client.send_message(
                chat_id=message.from_user.id,
                text="""
                This Files Will delete in 10min Please Forward To Saved Messages folder before download. \n\nTurned On /notification for get new movie|tv Serieses
                """)

            await asyncio.sleep(600)

            for k in sendmsglist:
                await k.delete()

            sendmsglist = []

            return await kk.delete()

        files_ = await get_file_details(file_id)
        if not files_:
            try:
                pre, file_id = ((base64.urlsafe_b64decode(
                    data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    protect_content=True if pre == 'filep' else False,
                )
                filetype = msg.media
                file = getattr(msg, filetype)
                title = file.file_name
                size = get_size(file.file_size)
                f_caption = f"<code>{title}</code>"
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(
                            file_name='' if title is None else title, file_size='' if size is None else size, file_caption='')
                    except:
                        return
                await msg.edit_caption(f_caption)
                return
            except:
                pass
            return await message.reply('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        k = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if pre == 'filep' else False,
        )
        sendmsglist = [k]
        await add_sent_files(message.from_user.id, file_id)

        files = await send_more_files(title)
        if files:
            for file in files[1:]:
                k = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file.file_id,
                    caption=f"<code>{file.file_name}</code>",
                    protect_content=True if pre == 'filep' else False,
                )
                sendmsglist.append(k)
                await add_sent_files(message.from_user.id, file.file_id)

                await asyncio.sleep(2)

            await message.reply("𝕋𝕙𝕒𝕟𝕜 𝕐𝕠𝕦 𝔽𝕠𝕣 𝕌𝕤𝕚𝕟𝕘 𝕄𝕖 \n\n⭐Rate Me: <a href='https://t.me/tlgrmcbot?start=spaciousuniversebot-review'>Here</a>")
            kk = await client.send_message(
                chat_id=message.from_user.id,
                text="""
                This Files Will delete in 10min Please Forward To Saved Messages folder before download. \n\nTurned On /notification for get new movie|tv Serieses
                """)

            await asyncio.sleep(600)

            for k in sendmsglist:
                await k.delete()
            sendmsglist = []

            return await kk.delete()

    user_stats = await get_verification(message.from_user.id)
    if user_stats is None:
        t = time.time()
        await add_verification(message.from_user.id, 'unverified', file_id, t)
        button = [[
            InlineKeyboardButton(
                '🔹 Verfiy 🔹', url=gen_url(f'https://telegram.dog/SpaciousUniverseBot?start=REAL-{data}'))
        ]]
        return await message.reply(
            text="""
            <p>you'r not verified today. verfied your self and get unlimited access</p>
            <br>
            <small><a href="kalanakt.github.io/projects/telegram/baesuzy/">How To Verify !</a></small>
            """,
            reply_markup=InlineKeyboardMarkup(button)
        )
    elif data.split("-", 1)[0] == "REAL":
        file_id = data.split("-", 1)[1]
        if (str(user_stats["stats"]) == 'unverified') and (str(user_stats["file"]) == file_id):
            file_id = data.split("-", 1)[1]
            t = time.time()
            await remove_verification(message.from_user.id)
            await add_verification(message.from_user.id, 'verified', file_id, t)
            t = time.localtime(t+43200)
            current_time = time.strftime("%D  %H:%M:%S", t)
            button = [[
                InlineKeyboardButton(
                    'Get Files', url=f'https://telegram.dog/SpaciousUniverseBot?start={file_id}')
            ]]
            return await message.reply(
                text=f"""
                <p>you'r verified Succusfully. access until {current_time}</p>
                """,
                reply_markup=InlineKeyboardMarkup(button)
            )
        elif data.split("-")[1] == "BATCH":
            file_id = data.split("-", 2)[2]
            t = time.time()
            await remove_verification(message.from_user.id)
            await add_verification(message.from_user.id, 'verified', file_id, t)
            t = time.localtime(t+43200)
            current_time = time.strftime("%D  %H:%M:%S", t)
            button = [[
                InlineKeyboardButton(
                    'Get Files', url=f'https://telegram.dog/SpaciousUniverseBot?start={file_id}')
            ]]
            return await message.reply(
                text=f"""
                <p>you'r verified Succusfully. access until {current_time}</p>
                """,
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            t = time.time()
            await remove_verification(message.from_user.id)
            await add_verification(message.from_user.id, 'unverified', file_id, t)
            t = time.localtime(t+43200)
            current_time = time.strftime("%D  %H:%M:%S", t)
            button = [[
                InlineKeyboardButton(
                    '🔹 Verfiy 🔹', url=gen_url(f'https://telegram.dog/SpaciousUniverseBot?start=REAL-{data}'))
            ]]
            return await message.reply(
                text=f"""
                <p>you'r using my old messages. please verify first</p>
                """,
                reply_markup=InlineKeyboardMarkup(button)
            )

    elif (str(user_stats["stats"]) == 'unverified') and (str(user_stats["file"]) != file_id):
        t = time.time()
        await remove_verification(message.from_user.id)
        await add_verification(message.from_user.id, 'unverified', file_id, t)
        button = [[
            InlineKeyboardButton(
                '🔹 Verfiy 🔹', url=gen_url(f'https://telegram.dog/SpaciousUniverseBot?start=REAL-{data}'))
        ]]
        return await message.reply(
            text="""
            <p>you'r not verified today. verfied your self and get unlimited access</p>
            <br>
            <small><a href="kalanakt.github.io/projects/telegram/baesuzy/">How To Verify !</a></small>
            """,
            reply_markup=InlineKeyboardMarkup(button)
        )

    elif (time.time() - int(float(user_stats["updat_time"]))) > 43200:
        t = time.time()
        await remove_verification(message.from_user.id)
        await add_verification(message.from_user.id, 'unverified', file_id, user_stats["updat_time"])
        button = [[
            InlineKeyboardButton(
                '🔹 Verfiy 🔹', url=gen_url(f'https://telegram.dog/SpaciousUniverseBot?start=REAL-{data}'))
        ]]
        return await message.reply(
            text="""
            <p>Your Verification Time Is expired. please verify again</p>
            <br>
            <small><a href="kalanakt.github.io/projects/telegram/baesuzy/">How To Verify</a></small>
            """,
            reply_markup=InlineKeyboardMarkup(button)
        )

    elif str(user_stats["stats"]) == 'verified':
        if data.split("-", 1)[0] == "BATCH":
            sts = await message.reply("Please wait")
            file_id = data.split("-", 1)[1]
            msgs = BATCH_FILES.get(file_id)
            sendmsglist = []
            if not msgs:
                file = await client.download_media(file_id)
                try:
                    with open(file) as file_data:
                        msgs = json.loads(file_data.read())
                except:
                    await sts.edit("FAILED")
                    return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
                os.remove(file)
                BATCH_FILES[file_id] = msgs
            for msg in msgs:
                title = msg.get("title")
                size = get_size(int(msg.get("size", 0)))
                f_caption = msg.get("caption", "")
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption = BATCH_FILE_CAPTION.format(
                            file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption = f_caption
                if f_caption is None:
                    f_caption = f"{title}"
                try:
                    k = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        protect_content=msg.get('protect', False),
                    )
                    sendmsglist.append(k)
                    await add_sent_files(message.from_user.id, msg.get("file_id"))

                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    logger.warning(f"Floodwait of {e.x} sec.")
                    k = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        protect_content=msg.get('protect', False),
                    )
                    sendmsglist.append(k)
                    await add_sent_files(message.from_user.id, msg.get("file_id"))

                except Exception as e:
                    logger.warning(e, exc_info=True)
                    continue
                await asyncio.sleep(2)
            await sts.delete()
            await message.reply("𝕋𝕙𝕒𝕟𝕜 𝕐𝕠𝕦 𝔽𝕠𝕣 𝕌𝕤𝕚𝕟𝕘 𝕄𝕖 \n\n⭐Rate Me: <a href='https://t.me/tlgrmcbot?start=spaciousuniversebot-review'>Here</a>")
            kk = await client.send_message(
                chat_id=message.from_user.id,
                text="""
                This Files Will delete in 10min Please Forward To Saved Messages folder before download. \n\nTurned On /notification for get new movie|tv Serieses
                """)

            await asyncio.sleep(600)

            for k in sendmsglist:
                await k.delete()
            sendmsglist = []

            return await kk.delete()

        elif data.split("-", 1)[0] == "DSTORE":
            sts = await message.reply("Please wait")
            b_string = data.split("-", 1)[1]
            decoded = (base64.urlsafe_b64decode(
                b_string + "=" * (-len(b_string) % 4))).decode("ascii")
            try:
                f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
            except:
                f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
                protect = "/pbatch" if PROTECT_CONTENT else "batch"
            diff = int(l_msg_id) - int(f_msg_id)
            async for msg in client.get_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
                if msg.media:
                    media = getattr(msg, msg.media)
                    if BATCH_FILE_CAPTION:
                        try:
                            f_caption = BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(
                                media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                        except Exception as e:
                            logger.exception(e)
                            f_caption = getattr(msg, 'caption', '')
                    else:
                        media = getattr(msg, msg.media)
                        file_name = getattr(media, 'file_name', '')
                        f_caption = getattr(msg, 'caption', file_name)
                    try:
                        k = await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                        await add_sent_files(message.from_user.id, message.chat.id)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        k = await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                        await add_sent_files(message.from_user.id, message.chat.id)
                    except Exception as e:
                        logger.exception(e)
                        continue
                elif msg.empty:
                    continue
                else:
                    try:
                        k = await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                        await add_sent_files(message.from_user.id, message.chat.id)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        k = await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                        await add_sent_files(message.from_user.id, message.chat.id)
                    except Exception as e:
                        logger.exception(e)
                        continue
                await asyncio.sleep(1)
            await sts.delete()
            await message.reply("𝕋𝕙𝕒𝕟𝕜 𝕐𝕠𝕦 𝔽𝕠𝕣 𝕌𝕤𝕚𝕟𝕘 𝕄𝕖 \n\n⭐Rate Me: <a href='https://t.me/tlgrmcbot?start=spaciousuniversebot-review'>Here</a>")
            kk = await client.send_message(
                chat_id=message.from_user.id,
                text="""
                This Files Will delete in 10min Please Forward To Saved Messages folder before download. \n\nTurned On /notification for get new movie|tv Serieses
                """)

            await asyncio.sleep(600)
            await k.delete()
            return await kk.delete()

        idstring = await get_ids(file_id)

        if idstring:
            await remove_inst(file_id)
            idstring = idstring['links']
            fileids = idstring.split("L_I_N_K")
            sendmsglist = []
            for file_id in fileids:
                files_ = await get_file_details(file_id)
                if not files_:
                    try:
                        msg = await client.send_cached_media(
                            chat_id=message.from_user.id,
                            file_id=file_id
                        )
                        filetype = msg.media
                        file = getattr(msg, filetype)
                        title = file.file_name
                        size = get_size(file.file_size)
                        f_caption = f"<code>{title}</code>"
                        if CUSTOM_FILE_CAPTION:
                            try:
                                f_caption = CUSTOM_FILE_CAPTION.format(
                                    file_name='' if title is None else title, file_size='' if size is None else size, file_caption='')
                            except:
                                return
                        await msg.edit_caption(f_caption)
                        return
                    except:
                        pass
                files = files_[0]
                title = files.file_name
                size = get_size(files.file_size)
                f_caption = files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(
                            file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption = f_caption
                if f_caption is None:
                    f_caption = f"{files.file_name}"
                try:
                    k = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=file_id,
                        caption=f_caption,
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    logger.warning(f"Floodwait of {e.x} sec.")
                    k = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=file_id,
                        caption=f_caption,
                    )
                sendmsglist.append(k)
                await add_sent_files(message.from_user.id, file_id)

                await asyncio.sleep(2)

            await message.reply('𝕋𝕙𝕒𝕟𝕜 𝕐𝕠𝕦 𝔽𝕠𝕣 𝕌𝕤𝕚𝕟𝕘 𝕄𝕖')
            kk = await client.send_message(
                chat_id=message.from_user.id,
                text="""
                This Files Will delete in 10min Please Forward To Saved Messages folder before download. \n\nTurned On /notification for get new movie|tv Serieses
                """)

            await asyncio.sleep(600)

            for k in sendmsglist:
                await k.delete()

            sendmsglist = []

            return await kk.delete()

        files_ = await get_file_details(file_id)
        if not files_:
            try:
                pre, file_id = ((base64.urlsafe_b64decode(
                    data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    protect_content=True if pre == 'filep' else False,
                )
                filetype = msg.media
                file = getattr(msg, filetype)
                title = file.file_name
                size = get_size(file.file_size)
                f_caption = f"<code>{title}</code>"
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(
                            file_name='' if title is None else title, file_size='' if size is None else size, file_caption='')
                    except:
                        return
                await msg.edit_caption(f_caption)
                return
            except:
                pass
            return await message.reply('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        k = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if pre == 'filep' else False,
        )
        sendmsglist = [k]
        await add_sent_files(message.from_user.id, file_id)

        files = await send_more_files(title)
        if files:
            for file in files[1:]:
                try:
                    k = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=file.file_id,
                        caption=f"<code>{file.file_name}</code>",
                        protect_content=True if pre == 'filep' else False,
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    logger.warning(f"Floodwait of {e.x} sec.")
                    k = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=file.file_id,
                        caption=f"<code>{file.file_name}</code>",
                        protect_content=True if pre == 'filep' else False,
                    )

                sendmsglist.append(k)
                await add_sent_files(message.from_user.id, file.file_id)
                await asyncio.sleep(2)

            await message.reply("𝕋𝕙𝕒𝕟𝕜 𝕐𝕠𝕦 𝔽𝕠𝕣 𝕌𝕤𝕚𝕟𝕘 𝕄𝕖 \n\n⭐Rate Me: <a href='https://t.me/tlgrmcbot?start=spaciousuniversebot-review'>Here</a>")
            kk = await client.send_message(
                chat_id=message.from_user.id,
                text="""
                This Files Will delete in 10min Please Forward To Saved Messages folder before download. \n\nTurned On /notification for get new movie|tv Serieses
                """)

            await asyncio.sleep(600)

            for k in sendmsglist:
                await k.delete()
            sendmsglist = []

            return await kk.delete()


@Client.on_message(filters.command("addseries") & filters.incoming & filters.user(ADMINS))
async def tvseries_adder(bot, message):
    sts = await message.reply("Checking Your Request...")
    if " " not in message.text:
        return await message.reply("Use correct format.<code>/addseries (name of series without space) (language eng/hindi/tamil/span) (quility 480/ 720/ 1080) (tv series batch links without space , use commas)</code>\n\n\nExample <code>/addseries strangerthings eng 480 https://tinyurl.com/23smxlh3,https://tinyurl.com/2yq2ghfh,https://tinyurl.com/27d9xyww,https://tinyurl.com/259az578</code>.")
    data = message.text.strip().split(" ")
    try:
        cmd, name, lang, quty, links = data
        await add_tvseries_filter(name, lang, quty, links)
        await message.reply("your series added")

    except:
        return await message.reply("May Be Error is you puts space between links: \nUse correct format.<code>/addseries (name of series without space) (language eng/hindi/tamil/span) (quility 480/ 720/ 1080) (tv series batch links without space , use commas)</code>\n\n\nExample <code>/addseries strangerthings eng 480 https://tinyurl.com/23smxlh3,https://tinyurl.com/2yq2ghfh,https://tinyurl.com/27d9xyww,https://tinyurl.com/259az578</code>.")
    await sts.delete()


@Client.on_message(filters.command("updateseries") & filters.incoming & filters.user(ADMINS))
async def tvseries_updater(bot, message):
    sts = await message.reply("Checking Your Request...")
    if " " not in message.text:
        return await message.reply("Use correct format.<code>/updateseries (name of series without space) (language eng/hindi/tamil/span) (quility 480/ 720/ 1080) (tv series batch links without space , use commas)</code>\n\n\nExample <code>/addseries strangerthings eng 480 https://tinyurl.com/23smxlh3,https://tinyurl.com/2yq2ghfh,https://tinyurl.com/27d9xyww,https://tinyurl.com/259az578</code>.")
    data = message.text.strip().split(" ")
    try:
        cmd, name, lang, quty, links = data
        await update_tvseries_filter(name, lang, quty, links)
        await message.reply("your series added")

    except:
        return await message.reply("May Be Error is you puts space between links: \nUse correct format.<code>/addseries (name of series without space) (language eng/hindi/tamil/span) (quility 480/ 720/ 1080) (tv series batch links without space , use commas)</code>\n\n\nExample <code>/addseries strangerthings eng 480 https://tinyurl.com/23smxlh3,https://tinyurl.com/2yq2ghfh,https://tinyurl.com/27d9xyww,https://tinyurl.com/259az578</code>.")
    await sts.delete()


@Client.on_message(filters.command("removeseries") & filters.incoming & filters.user(ADMINS))
async def tvseries_remover(bot, message):
    sts = await message.reply("Checking Your Request...")
    if " " not in message.text:
        return await message.reply("Use correct format.<code>/removeseries (name of series without space)")
    data = message.text.strip().split(" ")
    try:
        cmd, name = data
        await remove_tvseries(name)
        await message.reply("your series removed")

    except:
        return await message.reply("Not Found.")
    await sts.delete()


@Client.on_message(filters.command("alltvs") & filters.incoming)
async def tvseries_get(bot, message):
    k = await getlinks()
    await message.reply(k)


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):

    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('dev') & filters.user(ADMINS))
async def devve(bot, message):
    try:
        user_stats = await get_verification(message.from_user.id)
        await message.reply_text(user_stats)
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('notification') & filters.incoming)
async def get_notification(bot, message):
    await message.reply_text(
        'Get Movies/ Tv series On realse Time 〽. Turned on notifications, you can change anytime',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="On 🔛", callback_data="notification_on"
                    ),
                    InlineKeyboardButton(
                        text="Off 📴", callback_data="notification_off"
                    )
                ]
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^notification_on'))
async def notification_on(bot, query):
    user_id = query.from_user.id
    userStatus = await find_notification(user_id)
    if userStatus is None:
        await add_notification(user_id, 'on')
    else:
        await update_notification(user_id, 'on')

    return await query.message.edit('Succesfully Turned on notifications 💌. use /notification to change')


@Client.on_callback_query(filters.regex(r'^notification_off'))
async def notification_off(bot, query):
    user_id = query.from_user.id
    userStatus = await find_notification(user_id)
    if userStatus is None:
        await add_notification(user_id, 'off')
    else:
        await update_notification(user_id, 'off')
    return await query.message.edit('Succesfully Turned off notifications 💌. use /notification to change')


@Client.on_message(filters.command('sendnoti') & filters.user(ADMINS))
async def sendnotifications(bot, message):
    usersIdList = await find_allusers()
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply(f"Reply to message")
    count = 0
    msg = await message.reply("Processing...⏳", quote=True)
    for usersId in usersIdList:
        await broadcast_notification(usersId, b_msg)
        await asyncio.sleep(2)
        count += 1

    await msg.delete()
    return await message.reply(f"Succuesfully sended to {count} users")


@Client.on_message(filters.command('tmwad') & filters.user(ADMINS))
async def tmwad_update(bot, message):
    updates = await get_update_msg()
    if updates is not None:
        await remove_update_msg()
        prev_day_total_users = updates["totalUsers"]
        prev_day_total_files = updates["files"]

    else:
        return

    todaySentFiles = await count_sent_files()
    total_users = await db.total_users_count()
    files = await Media.count_documents()

    todayUsers = int(total_users) - int(prev_day_total_users)
    todayFiles = files - prev_day_total_files
    t = time.localtime()
    current_time = time.strftime("%D %H:%M:%S", t)

    await add_update_msg(total_users, files)

    try:
        await bot.edit_message_text(
            chat_id=str('TMWAD'),
            message_id=int(49),
            text=script.POST_TEXT.format(
                todaySentFiles, todayUsers, todayFiles, total_users, files, current_time)
        )
        return await message.reply("Update Succusfully on @TMWAD")
    except:
        logger.exception('Some error occured!', exc_info=True)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File is successfully deleted from database')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in ["group", "supergroup"]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Filter Button',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Single' if settings["button"] else 'Double',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Bot PM',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["botpm"] else '❌ No',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'File Secure',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["file_secure"] else '❌ No',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'IMDB',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["imdb"] else '❌ No',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Spell Check',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["spell_check"] else '❌ No',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Welcome',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["welcome"] else '❌ No',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>Change Your Settings for {title} As Your Wish ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            reply_to_message_id=message.id
        )


@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Checking template")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in ["group", "supergroup"]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("No Input!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"Successfully changed template for {title} to\n\n{template}")
