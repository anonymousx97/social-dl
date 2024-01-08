import asyncio
import glob
import importlib
import inspect
import os
import sys
import traceback
from functools import wraps
from io import BytesIO

from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from pyrogram.filters import Filter
from pyrogram.types import Message as Msg

from app import LOGGER, Config, Message
from app.utils import aiohttp_tools


def import_modules():
    for py_module in glob.glob(pathname="app/**/[!^_]*.py", recursive=True):
        name = os.path.splitext(py_module)[0]
        py_name = name.replace("/", ".")
        try:
            mod = importlib.import_module(py_name)
            if hasattr(mod, "init_task"):
                Config.INIT_TASKS.append(mod.init_task())
        except BaseException:
            LOGGER.error(traceback.format_exc())


class BOT(Client):
    def __init__(self):
        if string := os.environ.get("STRING_SESSION"):
            mode_arg = {"session_string": string}
        else:
            mode_arg = {"bot_token": os.environ.get("BOT_TOKEN")}
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
        from app.core.client.conversation import Conversation

        self.Convo = Conversation

    @staticmethod
    def add_cmd(cmd: str | list):
        def the_decorator(func):
            path = inspect.stack()[1][1]

            @wraps(func)
            def wrapper():
                if isinstance(cmd, list):
                    for _cmd in cmd:
                        Config.CMD_DICT[_cmd] = Config.CMD(
                            func=func, path=path, doc=func.__doc__
                        )
                else:
                    Config.CMD_DICT[cmd] = Config.CMD(
                        func=func, path=path, doc=func.__doc__
                    )

            wrapper()
            return func

        return the_decorator

    async def get_response(
        self, chat_id: int, filters: Filter = None, timeout: int = 8
    ) -> Message | None:
        try:
            async with self.Convo(
                chat_id=chat_id, filters=filters, timeout=timeout
            ) as convo:
                response: Message | None = await convo.get_response()
                return response
        except TimeoutError:
            return

    async def boot(self) -> None:
        await super().start()
        LOGGER.info("Started.")
        import_modules()
        LOGGER.info("Plugins Imported.")
        await asyncio.gather(*Config.INIT_TASKS)
        Config.INIT_TASKS.clear()
        LOGGER.info("Init Tasks Completed.")
        await self.log(text="<i>Started</i>")
        LOGGER.info("Idling...")
        await idle()
        await aiohttp_tools.init_task()

    async def log(
        self,
        text="",
        traceback="",
        chat=None,
        func=None,
        message: Message | Msg | None = None,
        name="log.txt",
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML,
    ) -> Message | Msg:
        if message:
            return (await message.copy(chat_id=Config.LOG_CHAT))  # fmt: skip
        if traceback:
            text = (
                "#Traceback"
                f"\n<b>Function:</b> {func}"
                f"\n<b>Chat:</b> {chat}"
                f"\n<b>Traceback:</b>"
                f"\n<code>{traceback}</code>"
            )
        return (await self.send_message(
            chat_id=Config.LOG_CHAT,
            text=text,
            name=name,
            disable_web_page_preview=disable_web_page_preview,
            parse_mode=parse_mode,
        ))  # fmt:skip

    async def restart(self, hard=False) -> None:
        await aiohttp_tools.init_task()
        await super().stop(block=False)
        if hard:
            os.remove("logs/app_logs.txt")
            os.execl("/bin/bash", "/bin/bash", "run")
        LOGGER.info("Restarting......")
        os.execl(sys.executable, sys.executable, "-m", "app")

    async def send_message(
        self, chat_id: int | str, text, name: str = "output.txt", **kwargs
    ) -> Message | Msg:
        text = str(text)
        if len(text) < 4096:
            return Message.parse_message(
                (await super().send_message(chat_id=chat_id, text=text, **kwargs))
            )
        doc = BytesIO(bytes(text, encoding="utf-8"))
        doc.name = name
        kwargs.pop("disable_web_page_preview", "")
        return await super().send_document(chat_id=chat_id, document=doc, **kwargs)
