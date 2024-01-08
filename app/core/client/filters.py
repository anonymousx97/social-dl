from urllib.parse import urlparse

from pyrogram import filters as _filters
from pyrogram.types import Message

from app import Config
from app.core.client.conversation import Conversation
from app.social_dl.media_handler import url_map

convo_filter = _filters.create(
    lambda _, __, message: (message.chat.id in Conversation.CONVO_DICT.keys())
    and (not message.reactions)
)


def check_for_urls(text_list: list):
    for link in text_list:
        if "music.youtube.com" in link:
            continue
        if url_map.get(urlparse(link).netloc):
            return True
        else:
            for key in url_map.keys():
                if key in link:
                    return True


def dynamic_chat_filter(_, __, message: Message, cmd=False) -> bool:
    if (
        not message.text
        or (not message.text.startswith("https") and not cmd)
        or message.chat.id not in Config.CHATS
        or (message.chat.id in Config.DISABLED_CHATS and not cmd)
        or message.forward_from_chat
    ):
        return False
    user = message.from_user
    if user and (user.id in Config.BLOCKED_USERS or user.is_bot):
        return False
    if cmd:
        return True
    url_check = check_for_urls(message.text.split())
    return bool(url_check)


chat_filter = _filters.create(dynamic_chat_filter)


def dynamic_allowed_list(_, __, message: Message) -> bool:
    if message.reactions or not dynamic_chat_filter(_, __, message, cmd=True):
        return False
    cmd = message.text.split(maxsplit=1)[0]
    return cmd in {"/download", "/dl", "/down"}


allowed_cmd_filter = _filters.create(dynamic_allowed_list)


def dynamic_cmd_filter(_, __, message: Message) -> bool:
    if (
        message.reactions
        or not message.text
        or not message.text.startswith(Config.CMD_TRIGGER)
        or not message.from_user
        or message.from_user.id not in Config.USERS
    ):
        return False
    start_str = message.text.split(maxsplit=1)[0]
    cmd = start_str.replace(Config.CMD_TRIGGER, "", 1)
    return cmd in Config.CMD_DICT.keys()


user_filter = _filters.create(dynamic_cmd_filter)
