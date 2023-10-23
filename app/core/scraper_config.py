import json
import shutil
from enum import Enum, auto
from io import BytesIO


class MediaType(Enum):
    PHOTO = auto()
    VIDEO = auto()
    GROUP = auto()
    GIF = auto()
    MESSAGE = auto()


class ScraperConfig:
    def __init__(self) -> None:
        self.dump: bool = False
        self.in_dump: bool = False
        self.path: str = ""
        self.media: str | BytesIO = ""
        self.caption: str = ""
        self.caption_url: str = ""
        self.thumb: str | None | BytesIO = None
        self.type: None | MediaType = None
        self.success: bool = False

    def __str__(self):
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False, default=str)

    def set_sauce(self, url: str) -> None:
        self.caption_url = f"\n\n<a href='{url}'>Sauce</a>"

    @classmethod
    async def start(cls, url: str) -> "ScraperConfig":
        obj = cls(url=url)
        obj.query_url = url
        obj.set_sauce(url)
        await obj.download_or_extract()
        if obj.success:
            return obj

    def cleanup(self) -> None:
        if self.path:
            shutil.rmtree(self.path, ignore_errors=True)
