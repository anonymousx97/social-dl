import asyncio
import json

from pyrogram.filters import Filter
from pyrogram.types import Message

from app import Config


class Conversation:
    class DuplicateConvo(Exception):
        def __init__(self, chat: str | int | None = None):
            text = "Conversation already started"
            if chat:
                text += f" with {chat}"
            super().__init__(text)

    class TimeOutError(Exception):
        def __init__(self):
            super().__init__("Conversation Timeout")

    def __init__(self, chat_id: int, filters: Filter | None = None, timeout: int = 10):
        self.chat_id = chat_id
        self.filters = filters
        self.timeout = timeout

    def __str__(self):
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False)

    async def get_response(self, timeout: int | None = None) -> Message | None:
        try:
            async with asyncio.timeout(timeout or self.timeout):
                while not Config.CONVO_DICT[self.chat_id]["response"]:
                    await asyncio.sleep(0)
            return Config.CONVO_DICT[self.chat_id]["response"]
        except asyncio.TimeoutError:
            raise self.TimeOutError

    async def __aenter__(self) -> "Conversation":
        if self.chat_id in Config.CONVO_DICT:
            raise self.DuplicateConvo(self.chat_id)
        convo_dict = {"filters": self.filters, "response": None}
        Config.CONVO_DICT[self.chat_id] = convo_dict
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        Config.CONVO_DICT.pop(self.chat_id, "")
