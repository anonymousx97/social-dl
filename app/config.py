import json
import os


class Config:
    API_KEYS = json.loads(os.environ.get("API_KEYS", "[]"))

    BLOCKED_USERS = []
    BLOCKED_USERS_MESSAGE_ID = int(os.environ.get("BLOCKED_USERS_MESSAGE_ID", 0))

    CHATS = []
    AUTO_DL_MESSAGE_ID = int(os.environ.get("AUTO_DL_MESSAGE_ID", 0))

    CMD_DICT = {}

    DEV_MODE = int(os.environ.get("DEV_MODE", 0))

    DISABLED_CHATS = []
    DISABLED_CHATS_MESSAGE_ID = int(os.environ.get("DISABLED_CHATS_MESSAGE_ID", 0))

    DUMP_ID = int(os.environ.get("DUMP_ID",0))

    LOG_CHAT = int(os.environ.get("LOG_CHAT"))
    TRIGGER = os.environ.get("TRIGGER", ".")

    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO","https://github.com/anonymousx97/social-dl").rstrip("/")

    USERS = []
    USERS_MESSAGE_ID = int(os.environ.get("USERS_MESSAGE_ID", 0))
