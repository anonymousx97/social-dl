import os
import json

class Config:
    API_KEYS = json.loads(os.envion.get("API_KEYS", "[]"))

    BLOCKED_USERS = []
    BLOCKED_USERS_MESSAGE_ID = int(os.environ.get("BLOCKED_USERS_MESSAGE_ID",0))

    CHATS = []
    AUTO_DL_MESSAGE_ID = int(os.environ.get("AUTO_DL_MESSAGE_ID",0))

    CMD_DICT = {}

    DEV_MODE = int(os.environ.get("DEV_MODE", 0))
    LOG_CHAT = int(os.environ.get("LOG_CHAT"))
    TRIGGER = os.environ.get("TRIGGER", ".")

    USERS = []
    USERS_MESSAGE_ID = int(os.environ.get("USERS_MESSAGE_ID",0))