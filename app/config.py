import json
import os
from typing import Callable

from pyrogram.filters import Filter
from pyrogram.types import Message


class Config:
    API_KEYS: list[int] = json.loads(os.environ.get("API_KEYS", "[]"))

    BLOCKED_USERS: list[int] = []
    BLOCKED_USERS_MESSAGE_ID: int = int(os.environ.get("BLOCKED_USERS_MESSAGE_ID", 0))

    CHATS: list[int] = []
    AUTO_DL_MESSAGE_ID: int = int(os.environ.get("AUTO_DL_MESSAGE_ID", 0))

    CMD_DICT: dict[str, Callable] = {}
    CONVO_DICT: dict[int, dict[str | int, Message | Filter | None]] = {}

    DEV_MODE: int = int(os.environ.get("DEV_MODE", 0))

    DISABLED_CHATS: list[int] = []
    DISABLED_CHATS_MESSAGE_ID: int = int(os.environ.get("DISABLED_CHATS_MESSAGE_ID", 0))

    DUMP_ID: int = int(os.environ.get("DUMP_ID", 0))

    LOG_CHAT: int = int(os.environ.get("LOG_CHAT"))

    TRIGGER: str = os.environ.get("TRIGGER", ".")

    UPSTREAM_REPO = os.environ.get(
        "UPSTREAM_REPO", "https://github.com/anonymousx97/social-dl"
    ).rstrip("/")

    USERS: list[int] = []
    USERS_MESSAGE_ID: int = int(os.environ.get("USERS_MESSAGE_ID", 0))
