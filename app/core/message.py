import asyncio
from functools import cached_property

from pyrogram.errors import MessageDeleteForbidden
from pyrogram.types import Message as MSG

from app import Config


class Message(MSG):
    def __init__(self, message):
        super().__dict__.update(message.__dict__)

    @cached_property
    def text_list(self):
        return self.text.split()

    @cached_property
    def reply_text_list(self):
        reply_text_list = []
        if (
            self.replied
            and (reply_text := self.replied.text)
            and "dl" in self.text_list[0]
        ):
            reply_text_list = self.replied.text_list
        return reply_text_list

    @cached_property
    def cmd(self):
        raw_cmd = self.text_list[0]
        cmd = raw_cmd.lstrip(Config.TRIGGER)
        return cmd if cmd in Config.CMD_DICT else None

    @cached_property
    def flags(self):
        return [i for i in self.text_list if i.startswith("-")]

    @cached_property
    def input(self):
        if len(self.text_list) > 1:
            return self.text.split(maxsplit=1)[-1]
        return ""

    @cached_property
    def flt_input(self):
        split_lines = self.input.splitlines()
        split_n_joined = [
            " ".join([word for word in line.split(" ") if word not in self.flags])
            for line in split_lines
        ]
        return "\n".join(split_n_joined)

    @cached_property
    def replied(self):
        if self.reply_to_message:
            return Message.parse_message(self.reply_to_message)

    @cached_property
    def reply_id(self):
        return self.replied.id if self.replied else None

    async def reply(self, text, del_in: int = 0, block=True, **kwargs):
        task = self._client.send_message(
            chat_id=self.chat.id, text=text, reply_to_message_id=self.id, **kwargs
        )
        if del_in:
            await self.async_deleter(task=task, del_in=del_in, block=block)
        else:
            return await task

    async def edit(self, text, del_in: int = 0, block=True, **kwargs):
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

    async def delete(self, reply=False):
        try:
            await super().delete()
            if reply and self.replied:
                await self.replied.delete()
        except MessageDeleteForbidden:
            pass

    async def async_deleter(self, del_in, task, block):
        if block:
            x = await task
            await asyncio.sleep(del_in)
            await x.delete()
        else:
            asyncio.create_task(
                self.async_deleter(del_in=del_in, task=task, block=True)
            )

    @classmethod
    def parse_message(cls, message):
        ret_obj = cls(message)
        return ret_obj
