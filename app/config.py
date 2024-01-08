import json
import os

from git import Repo


class _Config:
    class CMD:
        def __init__(self, func, path, doc):
            self.func = func
            self.path = path
            self.doc = doc or "Not Documented."

    def __init__(self):
        self.API_KEYS: list[int] = json.loads(os.environ.get("API_KEYS", "[]"))

        self.BLOCKED_USERS: list[int] = []
        self.BLOCKED_USERS_MESSAGE_ID: int = int(
            os.environ.get("BLOCKED_USERS_MESSAGE_ID", 0)
        )

        self.CHATS: list[int] = []
        self.AUTO_DL_MESSAGE_ID: int = int(os.environ.get("AUTO_DL_MESSAGE_ID", 0))

        self.CMD_TRIGGER: str = os.environ.get("TRIGGER", ".")

        self.CMD_DICT: dict[str, _Config.CMD] = {}

        self.DEV_MODE: int = int(os.environ.get("DEV_MODE", 0))

        self.DISABLED_CHATS: list[int] = []

        self.DISABLED_CHATS_MESSAGE_ID: int = int(
            os.environ.get("DISABLED_CHATS_MESSAGE_ID", 0)
        )

        self.DUMP_ID: int = int(os.environ.get("DUMP_ID", 0))

        self.INIT_TASKS: list = []

        self.LOG_CHAT: int = int(os.environ.get("LOG_CHAT"))

        self.REPO = Repo(".")

        self.UPSTREAM_REPO = os.environ.get(
            "UPSTREAM_REPO", "https://github.com/anonymousx97/social-dl"
        ).rstrip("/")

        self.USERS: list[int] = []
        self.USERS_MESSAGE_ID: int = int(os.environ.get("USERS_MESSAGE_ID", 0))

    def __str__(self):
        config_dict = self.__dict__.copy()
        return json.dumps(config_dict, indent=4, ensure_ascii=False, default=str)


Config = _Config()
