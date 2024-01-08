import asyncio
from functools import cached_property

from pyrogram.errors import MessageDeleteForbidden
from pyrogram.filters import Filter
from pyrogram.types import Message as Msg
from pyrogram.types import User

from app import Config


class Message(Msg):
    def __init__(self, message: Msg) -> None:
        args = vars(message).copy()
        args["client"] = args.pop("_client", message._client)
        super().__init__(**args)

    @cached_property
    def cmd(self) -> str | None:
        if not self.text_list:
            return
        raw_cmd = self.text_list[0]
        cmd = raw_cmd[1:]
        return (
            cmd
            if (
                cmd in Config.CMD_DICT.keys()
                or cmd in {"dl", "down", "download", "play", "song"}
            )
            else None
        )

    @cached_property
    def flags(self) -> list:
        return [i for i in self.text_list if i.startswith("-")]

    @cached_property
    def flt_input(self) -> str:
        split_lines = self.input.split("\n", maxsplit=1)
        split_lines[0] = " ".join(
            [word for word in split_lines[0].split(" ") if word not in self.flags]
        )
        return "\n".join(split_lines)

    @cached_property
    def input(self) -> str:
        if len(self.text_list) > 1:
            return self.text.split(maxsplit=1)[-1]
        return ""

    @cached_property
    def is_from_owner(self) -> bool:
        if self.from_user and self.from_user.id == Config.OWNER_ID:
            return True
        return False

    @cached_property
    def replied(self) -> "Message":
        if self.reply_to_message:
            return Message.parse_message(self.reply_to_message)

    @cached_property
    def reply_id(self) -> int | None:
        return self.replied.id if self.replied else None

    @cached_property
    def replied_task_id(self) -> str | None:
        return self.replied.task_id if self.replied else None

    @cached_property
    def reply_text_list(self) -> list:
        return self.replied.text_list if self.replied else []

    @cached_property
    def task_id(self):
        return f"{self.chat.id}-{self.id}"

    @cached_property
    def text_list(self) -> list:
        if self.text:
            return self.text.split()
        return []

    @cached_property
    def trigger(self):
        return Config.CMD_TRIGGER

    async def async_deleter(self, del_in, task, block) -> None:
        if block:
            x = await task
            await asyncio.sleep(del_in)
            await x.delete()
        else:
            asyncio.create_task(
                self.async_deleter(del_in=del_in, task=task, block=True)
            )

    async def delete(self, reply: bool = False) -> None:
        try:
            await super().delete()
            if reply and self.replied:
                await self.replied.delete()
        except MessageDeleteForbidden:
            pass

    async def edit(self, text, del_in: int = 0, block=True, **kwargs) -> "Message":
        if len(str(text)) < 4096:
            kwargs.pop("name", "")
            task = self.edit_text(text, **kwargs)
            if del_in:
                reply = await self.async_deleter(task=task, del_in=del_in, block=block)
            else:
                reply = await task
        else:
            _, reply = await asyncio.gather(
                super().delete(), self.reply(text, **kwargs)
            )
        return reply

    async def extract_user_n_reason(self) -> list[User | str | Exception, str | None]:
        if self.replied:
            return [self.replied.from_user, self.flt_input]
        inp_list = self.flt_input.split(maxsplit=1)
        if not inp_list:
            return [
                "Unable to Extract User info.\nReply to a user or input @ | id.",
                "",
            ]
        user = inp_list[0]
        reason = None
        if len(inp_list) >= 2:
            reason = inp_list[1]
        if user.isdigit():
            user = int(user)
        elif user.startswith("@"):
            user = user.strip("@")
        try:
            return [await self._client.get_users(user_ids=user), reason]
        except Exception as e:
            return [e, reason]

    async def get_response(self, filters: Filter = None, timeout: int = 8):
        try:
            async with self._client.Convo(
                chat_id=self.chat.id, filters=filters, timeout=timeout
            ) as convo:
                response: Message | None = await convo.get_response()
                return response
        except TimeoutError:
            return

    async def reply(
        self, text, del_in: int = 0, block: bool = True, **kwargs
    ) -> "Message":
        task = self._client.send_message(
            chat_id=self.chat.id, text=text, reply_to_message_id=self.id, **kwargs
        )
        if del_in:
            await self.async_deleter(task=task, del_in=del_in, block=block)
        else:
            return await task

    @classmethod
    def parse_message(cls, message: Msg) -> "Message":
        return cls(message)
