import asyncio
import json

from pyrogram.filters import Filter
from pyrogram.types import Message


class Conversation:
    CONVO_DICT: dict[int, "Conversation"] = {}

    class DuplicateConvo(Exception):
        def __init__(self, chat: str | int):
            super().__init__(f"Conversation already started with {chat} ")

    def __init__(
        self, chat_id: int | str, filters: Filter | None = None, timeout: int = 10
    ):
        self.chat_id = chat_id
        self.filters = filters
        self.timeout = timeout
        self.responses: list = []
        self.set_future()
        from app import bot

        self._client = bot

    def __str__(self):
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False, default=str)

    def set_future(self, *args, **kwargs):
        future = asyncio.Future()
        future.add_done_callback(self.set_future)
        self.response = future

    async def get_response(self, timeout: int | None = None) -> Message | None:
        try:
            resp_future: asyncio.Future.result = await asyncio.wait_for(
                self.response, timeout=timeout or self.timeout
            )
            return resp_future
        except asyncio.TimeoutError:
            raise TimeoutError("Conversation Timeout")

    async def send_message(
        self,
        text: str,
        timeout=0,
        get_response=False,
        **kwargs,
    ) -> Message | tuple[Message, Message]:
        message = await self._client.send_message(
            chat_id=self.chat_id, text=text, **kwargs
        )
        if get_response:
            response = await self.get_response(timeout=timeout or self.timeout)
            return message, response
        return message

    async def send_document(
        self,
        document,
        caption="",
        timeout=0,
        get_response=False,
        **kwargs,
    ) -> Message | tuple[Message, Message]:
        message = await self._client.send_document(
            chat_id=self.chat_id,
            document=document,
            caption=caption,
            force_document=True,
            **kwargs,
        )
        if get_response:
            response = await self.get_response(timeout=timeout or self.timeout)
            return message, response
        return message

    async def __aenter__(self) -> "Conversation":
        if isinstance(self.chat_id, str):
            self.chat_id = (await self._client.get_chat(self.chat_id)).id
        if (
            self.chat_id in Conversation.CONVO_DICT.keys()
            and Conversation.CONVO_DICT[self.chat_id].filters == self.filters
        ):
            raise self.DuplicateConvo(self.chat_id)
        Conversation.CONVO_DICT[self.chat_id] = self
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        Conversation.CONVO_DICT.pop(self.chat_id, None)
        if not self.response.done():
            self.response.cancel()
