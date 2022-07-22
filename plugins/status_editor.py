from Script import script
import time
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import temp
from database.quickdb import count_sent_files, add_update_msg, remove_update_msg, get_verification
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

btn = [
    [
        InlineKeyboardButton("Developer", url="https://github.com/kalanakt"),
        InlineKeyboardButton("Join Group", url="https://t.me/TMWAD_Support")
    ]
]


@Client.on_message(filters.chat('TMWAD'))
async def stats_channel(client, message):
    while True:
        updates = await get_verification()
        await remove_update_msg()
        todaySentFiles = await count_sent_files()
        total_users = await db.total_users_count()
        files = await Media.count_documents()
        prev_day_total_users = updates["totalUsers"]
        prev_day_total_files = updates["updatemsg"]
        todayUsers = total_users - prev_day_total_users
        todayFiles = files - prev_day_total_files
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        await add_update_msg(todaySentFiles, total_users, files)

        try:
            await client.edit_message_text(
                chat_id=str('TMWAD'),
                message_id=int(49),
                text=script.POST_TEXT.format(
                    todaySentFiles, todayUsers, todayFiles, total_users, files, current_time),
                reply_markup=InlineKeyboardMarkup(btn),
            )
            logger.exception(
                todaySentFiles, todayUsers, todayFiles, total_users, files, current_time)
        except:
            logger.exception('Some error occured!', exc_info=True)

        await asyncio.sleep(86400)
