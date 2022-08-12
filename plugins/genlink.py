import re
from pyrogram import filters, Client
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import unpack_new_file_id
from utils import temp
import re
import os
import json
import base64
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    return bool(message.from_user and message.from_user.id in ADMINS)

FILE_STORE_CHANNEL = ["-1001383308476"]


@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    logger.info(message.text)
    if " " not in message.text:
        return await message.reply("Use correct format.\nExample <code>/batch https://t.me/TeamEvamaria/10 https://t.me/TeamEvamaria/20</code>.")

    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply("Use correct format.\nExample <code>/batch https://t.me/TeamEvamaria/10 https://t.me/TeamEvamaria/20</code>.")

    cmd, first, last = links
    regex = re.compile(
        "(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    match = regex.match(first)
    if not match:
        return await message.reply('Invalid link')
    f_chat_id = match.group(4)
    f_msg_id = int(match.group(5))
    match = regex.match(last)
    l_chat_id = match.group(4)
    l_msg_id = int(match.group(5))
    blimit = abs(l_msg_id - f_msg_id)
    if f_chat_id.isnumeric():
        f_chat_id = int(f"-100{f_chat_id}")
    if not match:
        return await message.reply('Invalid link')
    if l_chat_id.isnumeric():
        l_chat_id = int(f"-100{l_chat_id}")
    if f_chat_id != l_chat_id:
        return await message.reply("Chat ids not matched.")
    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')

    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')
    sts = await message.reply("Generating link for your message.\nThis may take time depending upon number of messages")

    if chat_id not in FILE_STORE_CHANNEL:
        return await sts.edit(f"Here is your link https://t.me/{chat_id}?start=DSTORE-{FILE_STORE_CHANNEL}")

    string = f"{f_msg_id}_{l_msg_id}_{chat_id}_{cmd.lower().strip()}"
    b_64 = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    return await sts.edit(f"Here is your link https://t.me/{temp.U_NAME}?start=DSTORE-{b_64}")
