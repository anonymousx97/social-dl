import json
import shutil
from io import BytesIO

from pyrogram.types import Message

from app import bot
from app.utils.aiohttp_tools import thumb_dl
from app.utils.media_helper import MediaType


class ScraperConfig:
    def __init__(self, url) -> None:
        self.caption: str = ""
        self.dump: bool = False
        self.in_dump: bool = False
        self.media: str | BytesIO | list[str, BytesIO] | Message = ""
        self.path: str | list[str] = ""
        self.raw_url: str = url
        self.sauce: str = ""
        self.success: bool = False
        self.thumb: str | None | BytesIO = None
        self.type: None | MediaType = None

    def __str__(self):
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False, default=str)

    async def download_or_extract(self):
        ...

    async def get_coro(self, **kwargs) -> tuple:
        if self.type == MediaType.VIDEO:
            return (
                bot.send_video,
                dict(**kwargs, video=self.media, thumb=await thumb_dl(self.thumb)),
                "video",
            )
        if self.type == MediaType.PHOTO:
            return bot.send_photo, dict(**kwargs, photo=self.media), "photo"
        if self.type == MediaType.GIF:
            return (
                bot.send_animation,
                dict(**kwargs, animation=self.media, unsave=True),
                "animation",
            )

    def set_sauce(self, url: str) -> None:
        self.sauce = f"\n\n<a href='{url}'>Sauce</a>"

    @classmethod
    async def start(cls, url: str) -> "ScraperConfig":
        obj = cls(url=url)
        obj.set_sauce(url)
        await obj.download_or_extract()
        if obj.success:
            return obj

    def cleanup(self) -> None:
        if self.path:
            shutil.rmtree(self.path, ignore_errors=True)
