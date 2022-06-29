import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import AUTH_CHANNEL, LONG_IMDB_DESCRIPTION, MAX_LIST_ELM
from imdb import IMDb
import asyncio
from pyrogram.types import Message
from typing import Union
import re
import os
import pyshorteners
from datetime import datetime
from typing import List
from pyrogram.types import InlineKeyboardButton
from database.users_chats_db import db
from plugins.advance_filters import namelist, linklist
from Sewlink import *
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

imdb = IMDb() 
url_shortener = pyshorteners.Shortener()

BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)
btns = []

# temp db for banned 
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}

async def is_subscribed(bot, query):
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if user.status != 'kicked':
            return True

    return False


async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1]) 
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid=list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movieid}'
    }
# https://github.com/odysseusm


async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Succes"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"

async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
        }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    response = requests.get(url, headers=usr_agent)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all( 'h3' )
    return [title.getText() for title in titles]

async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS[group_id] = settings
    return settings

async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)
    
def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def get_name(name):
    name = name.lower()
    name = name.replace("@cc", '')
    name = name.replace("telegram", '')
    name = name.replace("www", '')
    name = name.replace("join", '')
    name = name.replace("tg", '')
    name = name.replace("link", '') 
    name = name.replace("@", '')
    name = name.replace("massmovies0", '')
    name = name.replace("bullmoviee", '')
    name = name.replace("massmovies", '')
    name = name.replace("filmy4cab", '')
    name = name.replace("maassmovies",'')
    name = name.replace("theproffesorr",'')
    name = name.replace("primeroom",'')
    name = name.replace("team_hdt",'')
    name = name.replace("telugudubbing", '')
    name = name.replace("rickychannel", '')
    name = name.replace("tif", '')
    name = name.replace("cvm", '')
    name = name.replace("playtk", '')
    name = name.replace("tel", '')
    name = name.replace("hw", '')
    name = name.replace("f&t", '')
    name = name.replace("fimy", '')
    name = name.replace("film", '')
    name = name.replace("xyz", '')
    name = name.replace("fbm", '')
    name = name.replace("mwkott", '')
    name = name.replace("team_hdt", '')
    name = name.replace("worldcinematoday", '')
    name = name.replace("cinematic_world", '')
    name = name.replace("cinema", '')
    name = name.replace("hotstar", '')
    name = name.replace("jesseverse", '')
    name = name.replace("apdackup", '')
    name = name.replace("streamersHub", '')
    name = name.replace("tg", '')
    name = name.replace("movies", '')
    name = name.replace("[ava]", '')
    name = name.replace("tamilrockers", '')
    name = name.replace("imax5", '')
    name = name.replace("kerala rock", '')
    name = name.replace("ott", '')
    name = name.replace("rarefilms", '')
    name = name.replace("linkzz", '')
    name = name.replace("movems", '')
    name = name.replace("moviezz", '')
    name = name.replace("clipmate", '')
    name = name.replace("southtamilall", '')
    name = name.replace("apdbackup", '')
    name = name.replace("wmr", '')
    name = name.replace("web", '')
    name = name.replace("rowdystudios", '')
    name = name.replace("alpacinodump", '')
    name = name.replace("fans", '')
    name = name.replace("movie", '')
    name = name.replace("mlf", '')
    name = name.replace("[rmk]", '')
    name = name.replace("[mc]", '')
    name = name.replace("[mfa]", '')
    name = name.replace("[mm]", '')
    name = name.replace("[me]", '')
    name = name.replace("[", '')
    name = name.replace("]", '')
    name = name.replace("mlm", '')
    name = name.replace("RMK", '')
    name = name.replace("1tamilmv", '')
    name = name.replace("linkz", '')
    name = name.replace("tamilMob", '')
    name = name.replace("tg", '')
    name = name.replace("bollyarchives", '')
    name = name.replace("🎞", '')
    name = name.replace("🎬", '')
    name = name.replace("(", '')
    name = name.replace(")", '')
    name = name.replace(" ", '.')
    name = name.replace("_", '.')
    name = name.replace("...", '.')
    name = name.replace("..", '.')

    if name[0] == '.':
        name = name[1:]
    name = name.capitalize()
    return name

def get_url(fileid):
    ident, file_id = fileid.split("#")
    urllink = f'https://shorturllink.in/st?api=3ef6a62253efbe7a63dd29201b2f9c661bd15795&url=https://telegram.dog/SpaciousUniverseBot?start={ident}_{file_id}'   
    urllink = url_shortener.tinyurl.short(urllink)
    return urllink

def getseries(name):
    name = name.lower()
    name = name.replace("season", "")
    name = name.replace("series", "")
    name = name.replace("tv", "")
    name = name.replace("episode", "")
    name = name.replace("480p", "")
    name = name.replace("720p", "")
    name = name.replace("1080p", "")
    name = name.replace("hindi", "")
    name = name.replace("tamil", "")
    name = name.replace("english", "")
    name = name.replace("web", "")
    name = ''.join([i for i in name if not i.isdigit()])
    name = name.replace(" ","")

    return name

def statusLinks(name):
    if name in namelist:     
        return True
    else:
        return False

def gettitle(name):
    if name == 'e4':
        name = '『    English |  480p    』'
    elif name == 'e7':
        name = '『    English |  720p    』'
    elif name == 'e108':
        name = '『    English |  1080p    』'
    elif name == 'h4':
        name = '『    Hindi |  480p    』'
    elif name == 'h7':
        name = '『    Hindi |  720p    』'
    elif name == 'h108':
        name = '『    Hindi |  1080p    』'
    elif name == 's4':
        name = '『    Spanish |  480p    』'
    elif name == 's7':
        name = '『    Spanish |  720p    』'
    elif name == 's108':
        name = '『    Spanish |  1080p    』'
    elif name == 't4':
        name = '『    Tamil |  480p    』'
    elif name == 't7':
        name = '『    Tamil |  720p    』'
    elif name == 't108':
        name = '『    Tamil |  1080p    』'
    elif name == 'k4':
        name = '『    Korean |  480p    』'
    elif name == 'k7':
        name = '『    Korean |  720p    』'
    elif name == 'k108':
        name = '『    Korean |  1080p    』'

    return name

def getbtn(name):
    btns = []
    bn = []
    index = namelist.index(name)
    links = linklist[index]
    x = 1
    s = 0

    for i in links:
        for j in i:
            if j in ['e4','h4','s4','t4','e7','h7','t7','s7','e108', 'h108','t108','s108']:
                if x > 1:
                    btns.append(bn)
                    bn = []
                    s = 0

                btns.append(
                    [
                        InlineKeyboardButton(
                            text=f"{gettitle(j)}", callback_data="seriestitle"
                            )
                    ]
                )

            else:
                link = Links[f'{j}']
                url1 = 'https://shorturllink.in/st?api=3ef6a62253efbe7a63dd29201b2f9c661bd15795&url='
                urllink = f'{url1}{link}'                  
                urllink = url_shortener.tinyurl.short(urllink)
                bn.append(
                     InlineKeyboardButton(
                        text=f"Season {s}",
                        url=urllink
                    )
                )

                if (len(bn) > 2):
                    btns.append(bn)
                    bn = []
            s += 1
            x += 1 

    btns.append(bn)

    return btns
                
def geturl(fileid):
    urllink = f'https://shorturllink.in/st?api=3ef6a62253efbe7a63dd29201b2f9c661bd15795&url=https://telegram.dog/SpaciousUniverseBot?start={fileid}'   
    urllink = url_shortener.tinyurl.short(urllink)
    return urllink

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n] 

def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    # https://github.com/SpEcHiDe/PyroGramBot/blob/f30e2cca12002121bad1982f68cd0ff9814ce027/pyrobot/helper_functions/extract_user.py#L7
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == "text_mention"
        ):
           
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            # don't want to make a request -_-
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def last_online(from_user):
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot :("
    elif from_user.status == 'recently':
        time += "Recently"
    elif from_user.status == 'within_week':
        time += "Within the last week"
    elif from_user.status == 'within_month':
        time += "Within the last month"
    elif from_user.status == 'long_time_ago':
        time += "A long time ago :("
    elif from_user.status == 'online':
        time += "Currently Online"
    elif from_user.status == 'offline':
        time += datetime.fromtimestamp(from_user.last_online_date).strftime("%a, %d %b %Y, %H:%M:%S")
    return time


def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    # 1 to avoid starting quote, and counter is exclusive so avoids ending
    key = remove_escapes(text[1:counter].strip())
    # index will be in range, or `else` would have been executed and returned
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                # create a thruple with button label, url, and newline status
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'
