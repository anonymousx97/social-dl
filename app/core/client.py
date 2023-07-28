import glob
import importlib
import json
import os
import sys
from functools import wraps
from io import BytesIO

from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from app import Config
from app.core import aiohttp_tools

from app.core.message import Message


class BOT(Client):

    def __init__(self):
        if string := os.environ.get("STRING_SESSION"):
            mode_arg = { "session_string": string }
        else:
            mode_arg = { "bot_token": os.environ.get("BOT_TOKEN") }
        super().__init__(
            name="bot",
            **mode_arg,
            api_id=int(os.environ.get("API_ID")),
            api_hash=os.environ.get("API_HASH"),
            in_memory=True,
            parse_mode=ParseMode.DEFAULT,
            sleep_threshold=30,
            max_concurrent_transmissions=2,
        )

    def add_cmd(self, cmd, trigger=Config.TRIGGER):  # Custom triggers To do
        def the_decorator(func):
            @wraps(func)
            def wrapper():
                Config.CMD_DICT[cmd] = func

            wrapper()
            return func

        return the_decorator

    async def boot(self):
        await super().start()
        await self.import_modules()
        await self.set_filter_list()
        await aiohttp_tools.session_switch()
        await self.edit_restart_msg()
        await self.log(text="#Social-dl\n__Started__")
        print("started")
        await idle()
        await aiohttp_tools.session_switch()

    async def edit_restart_msg(self):
        restart_msg = os.environ.get("RESTART_MSG")
        restart_chat = os.environ.get("RESTART_CHAT")
        if restart_msg and restart_chat:
            await super().get_chat(int(restart_chat))
            await super().edit_message_text(chat_id=int(restart_chat), message_id=int(restart_msg), text="#Social-dl\n__Started__")
            os.environ.pop("RESTART_MSG", "")
            os.environ.pop("RESTART_CHAT", "")

    async def import_modules(self):
        for py_module in glob.glob("app/**/*.py", recursive=True):
            name = os.path.splitext(py_module)[0]
            py_name = name.replace("/", ".")
            importlib.import_module(py_name)

    async def log(self, text, chat=None, func=None, name="log.txt",disable_web_page_preview=True):
        if chat or func:
            text = f"<b>Function:</b> {func}\n<b>Chat:</b> {chat}\n<b>Traceback:</b>\n{text}"
        return await self.send_message(chat_id=Config.LOG_CHAT, text=text, name=name, disable_web_page_preview=disable_web_page_preview)

    async def restart(self):
        await aiohttp_tools.session_switch()
        await super().stop(block=False)
        os.execl(sys.executable, sys.executable, "-m", "app")

    async def set_filter_list(self):
        chats_id = Config.AUTO_DL_MESSAGE_ID
        blocked_id = Config.BLOCKED_USERS_MESSAGE_ID
        users = Config.USERS_MESSAGE_ID

        if chats_id:
            Config.CHATS = json.loads((await super().get_messages(Config.LOG_CHAT, chats_id)).text)
        if blocked_id:
            Config.BLOCKED_USERS = json.loads((await super().get_messages(Config.LOG_CHAT, blocked_id)).text)
        if users:
            Config.USERS = json.loads((await super().get_messages(Config.LOG_CHAT, users)).text)


    async def send_message(self, chat_id, text, name: str = "output.txt", **kwargs):
        if len(str(text)) < 4096:
            return Message.parse_message((await super().send_message(chat_id=chat_id, text=text, **kwargs)))
        doc = BytesIO(bytes(text, encoding="utf-8"))
        doc.name = name
        kwargs.pop("disable_web_page_preview", "")
        return await super().send_document(chat_id=chat_id, document=doc, **kwargs)
