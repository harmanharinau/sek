from distutils.log import error
import logging
import asyncio
from queue import Empty
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


@Client.on_callback_query(filters.regex('^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user), f'Your Submission for indexing {chat} has been decliened by our moderators.', reply_to_message_id=int(lst_msg_id))

        return
    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)

    msg = query.message
    await query.answer('Processing...⏳', show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user), f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.', reply_to_message_id=int(lst_msg_id))

    await msg.edit("Starting Indexing", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]))

    try:
        chat = int(chat)
    except Exception:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message(filters.forwarded & filters.private & filters.incoming)
async def send_for_index(bot, message):
    last_msg_id = message.forward_from_message_id
    chat_id = message.forward_from_chat.id
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'Errors - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except Exception:
        return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
    if k.empty:
        return await message.reply('This may be group and iam not a admin of the group.')

    if message.from_user.id in ADMINS:
        buttons = [
            [
                InlineKeyboardButton('Yes',
                                     callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
            ],
            [
                InlineKeyboardButton('close', callback_data='close_data'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f'Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>',
            reply_markup=reply_markup)

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Make sure iam an admin in the chat and have permission to invite users.')
    else:
        link = f"@{message.forward_from_chat.username}"
    buttons = [
        [
            InlineKeyboardButton('Accept Index',
                                 callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
        ],
        [
            InlineKeyboardButton('Reject Index',
                                 callback_data=f'index#reject#{chat_id}#{message.message_id}#{message.from_user.id}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(LOG_CHANNEL,
                           f'#IndexRequest\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/ Username - <code> {chat_id}</code>\nLast Message ID - <code>{last_msg_id}</code>\nInviteLink - {link}',
                           reply_markup=reply_markup)
    await message.reply('ThankYou For the Contribution, Wait For My Moderators to verify the files.')


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    errors, total_files, duplicate, deleted, no_media, unsupported = 0, 0, 0, 0, 0, 0
    try:
        for _ in range(abs(lst_msg_id)):
            message = await bot.get_messages(chat, lst_msg_id)
            if message.empty:
                no_media += 1
                continue
            for file_type in ("document", "video", "audio"):
                media = getattr(message, file_type, None)
            if not media:
                unsupported += 1
                continue
            media.file_type = message.media
            media.caption = message.caption
            aynav, vnay = await save_file(media)
            await msg.edit(aynav, vnay)
            lst_msg_id += 1

    except Exception as e:
        logger.exception(e)
        await msg.edit(f'Error: {e}')
    else:
        await msg.edit(f'Succesfully saved <code>{total_files}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>')
