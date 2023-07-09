from pyrogram.types import Message as MSG


class Message(MSG):
    def __init__(self, message):
        self.flags = []
        self.input, self.flt_input = "", ""
        self.replied, self.reply_id = None, None
        super().__dict__.update(message.__dict__)
        self.set_reply_properties()
        self.flags_n_input()
        self.set_flt_input()

    @property
    def get_text_list(self):
        text_list = self.text.split()
        if self.replied and (reply_text := self.replied.text) and "dl" in text_list[0]:
            text_list.extend(reply_text.split())
        return text_list

    def set_reply_properties(self):
        if replied := self.reply_to_message:
            self.replied = replied
            self.reply_id = replied.id

    def flags_n_input(self):
        self.flags = [i for i in self.text.split() if i.startswith("-")]
        split_cmd_str = self.text.split(maxsplit=1)
        if len(split_cmd_str) > 1:
            self.input = split_cmd_str[-1]

    def set_flt_input(self):
        line_split = self.input.splitlines()
        split_n_joined =[
            " ".join([word for word in line.split(" ") if word not in self.flags]) 
            for line in line_split
        ]
        self.flt_input = "\n".join(split_n_joined)

    async def reply(self, text, **kwargs):
        return await self._client.send_message(chat_id=self.chat.id, text=text, reply_to_message_id=self.id, **kwargs)

    async def edit(self, text, **kwargs):
        if len(str(text)) < 4096:
            kwargs.pop("name", "")
            await self.edit_text(text, **kwargs)
        else:
            await super().delete()
            return await self.reply(text, **kwargs)

    async def delete(self, reply=False):
        await super().delete()
        if reply and self.replied:
            await self.replied.delete()

    @classmethod
    def parse_message(cls, message):
        ret_obj = cls(message)
        return ret_obj
