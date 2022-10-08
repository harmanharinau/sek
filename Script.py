class script(object):
    START_TXT = """ℍ𝕖𝕝𝕝𝕠 {},
𝕀𝕞 <a href=https://t.me/{}>{}</a>, 𝕁𝕦𝕤𝕥 𝔸𝕕𝕕 𝕄𝕖 𝕋𝕠 𝕐𝕠𝕦𝕣 𝔾𝕣𝕠𝕦𝕡𝕤 𝕋𝕠 𝔼𝕒𝕣𝕟 𝕐𝕠𝕦𝕣 ℙ𝕣𝕠𝕗𝕚𝕥 💸"""
    HELP_TXT = """
How To Use Bot ? 🔘
To Use Ldisk Movie Search You Just Have A Account In sundisk.in |
Go To Dashboard -> Menu -> Tools -> Devoloper Api . 
Copy The Api And Add Ldisk Search Bot In Group .
To Connect Your Api Give Command /add_api your api  .
Now Enjoy Your Profit 💸."""
    ABOUT_TXT = """
Welcome To sundisk.in
This is the free link Converter. Just sign up through our website and then login and short your link and Share your shorten links and earn money 💰.
To Use The Bots You Just Have to Login in sundisk.in  And Go To Devolopers Api Copy And send To Bot easy (. ❛ ᴗ ❛.)
Also We Are Making Some More Awesome Bots To Make Your Hard Work Low 😉 Enjoy.
Site Link - sundisk.in
Signup page link - https://sundisk.in/auth/signup
To know more details visit our channel - @"""
    SOURCE_TXT = """
    NOTE:
Current CPM - $1 (About 75-80Rs)
Minimum Withdrawal Ammount Is 2-5$ For Defferent Withdrawal Types

UPI $1.0000
Paytm $1.0000
Phone Pe $1.0000
GooglePay $1.0000
Bank Transfer(INDIA) $1.0000
PayPal $5.0000

Other Payment Methods Comeing Soon 
More INFO - https://sundisk.in/member/users/profile
"""
    MANUELFILTER_TXT = """Help: <b>Filters</b>
- Filter is the feature were users can set automated replies for a particular keyword and EvaMaria will respond whenever a keyword is found the message
<b>NOTE:</b>
1. eva maria should have admin privillage.
2. only admins can add filters in a chat.
3. alert buttons have a limit of 64 characters.
<b>Commands and Usage:</b>
• /filter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>"""

    BUTTON_TXT = """Help: <b>Buttons</b>
- Eva Maria Supports both url and alert inline buttons.
<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. Eva Maria supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format
<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/EvaMariaBot)</code>
<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""

    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>
<b>NOTE:</b>
1. Make me the admin of your channel if it's private.
2. make sure that your channel does not contains camrips, porn and fake files.
3. Forward the last message to me with quotes.
 I'll add all the files in that channel to my db."""

    CONNECTION_TXT = """Help: <b>Connections</b>
- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.
<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM
<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""

    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>
<b>NOTE:</b>
these are the extra features of Eva Maria
<b>Commands and Usage:</b>
• /id - <code>get id of a specified user.</code>
• /info  - <code>get information about a user.</code>
• /imdb  - <code>get the film information from IMDb source.</code>
• /search  - <code>get the film information from various sources.</code>"""

    ADMIN_TXT = """Help: <b>Admin mods</b>
<b>NOTE:</b>
This module only works for my admins
<b>Commands and Usage:</b>
• /logs - <code>to get the rescent errors</code>
• /stats - <code>to get status of files in db.</code>
• /delete - <code>to delete a specific file from db.</code>
• /users - <code>to get list of my users and ids.</code>
• /chats - <code>to get list of the my chats and ids </code>
• /leave  - <code>to leave from a chat.</code>
• /disable  -  <code>do disable a chat.</code>
• /ban  - <code>to ban a user.</code>
• /unban  - <code>to unban a user.</code>
• /channel - <code>to get list of total connected channels</code>
• /broadcast - <code>to broadcast a message to all users</code>"""

    STATUS_TXT = """★ 𝚃𝙾𝚃𝙰𝙻 𝙵𝙸𝙻𝙴𝚂: <code>{}</code>
★ 𝚃𝙾𝚃𝙰𝙻 𝚄𝚂𝙴𝚁𝚂: <code>{}</code>
★ 𝚃𝙾𝚃𝙰𝙻 𝙲𝙷𝙰𝚃𝚂: <code>{}</code>
★ 𝚄𝚂𝙴𝙳 𝚂𝚃𝙾𝚁𝙰𝙶𝙴: <code>{}</code> 𝙼𝚒𝙱
★ 𝙵𝚁𝙴𝙴 𝚂𝚃𝙾𝚁𝙰𝙶𝙴: <code>{}</code> 𝙼𝚒𝙱"""

    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}"""
