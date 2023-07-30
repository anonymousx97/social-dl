from urllib.parse import urlparse

from pyrogram import filters as _filters

from app import Config
from app.core.MediaHandler import url_map


def Dynamic_Chat_Filter(_, __, message):
    if (
        not message.text
        or not message.text.startswith("https")
        or message.chat.id not in Config.CHATS
        or message.forward_from_chat
    ):
        return False
    user = message.from_user
    if user and (user.id in Config.BLOCKED_USERS or user.is_bot):
        return False
    url_check = check_for_urls(message.text.split())
    return bool(url_check)


def check_for_urls(text_list):
    for link in text_list:
        if match := url_map.get(urlparse(link).netloc):
            return True
        else:
            for key in url_map.keys():
                if key in link:
                    return True


def Dynamic_Cmd_Filter(_, __, message):
    if (
        not message.text
        or not message.text.startswith(Config.TRIGGER)
        or not message.from_user
        or message.from_user.id not in Config.USERS
    ):
        return False

    start_str = message.text.split(maxsplit=1)[0]
    cmd = start_str.replace(Config.TRIGGER, "", 1)
    cmd_check = cmd in Config.CMD_DICT
    reaction_check = not message.reactions
    return bool(cmd_check and reaction_check)


chat_filter = _filters.create(Dynamic_Chat_Filter)
user_filter = _filters.create(Dynamic_Cmd_Filter)
