from urllib.parse import urlparse

from pyrogram import filters as _filters

from app import Config
from app.core.MediaHandler import url_map


def DYNAMIC_CHAT_FILTER(_, __, message):
    if not message.text or not message.text.startswith("https"):
        return False
    chat_check = message.chat.id in Config.CHATS
    user_check = True
    if user := message.from_user:
        user_check = user.id not in Config.BLOCKED_USERS and not user.is_bot
    return bool(chat_check and user_check and check_for_urls(message.text.split()))


def check_for_urls(text_list):
    for link in text_list:
        if match := url_map.get(urlparse(link).netloc):
            return True
        else:
            for key in url_map.keys():
                if key in link:
                    return True


def DYNAMIC_CMD_FILTER(_, __, message):
    if not message.text or not message.text.startswith(Config.TRIGGER):
        return False
    cmd_check = message.text.split(maxsplit=1)[0].replace(Config.TRIGGER, "", 1) in Config.CMD_DICT
    user_check = False
    if user := message.from_user:
        user_check = user.id in Config.USERS
    reaction_check = bool(not message.reactions)
    return bool(cmd_check and user_check and reaction_check)


chat_filter = _filters.create(DYNAMIC_CHAT_FILTER)
user_filter = _filters.create(DYNAMIC_CMD_FILTER)
