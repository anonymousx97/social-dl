import shutil
from enum import Enum, auto


class MediaType(Enum):
    PHOTO = auto()
    VIDEO = auto()
    GROUP = auto()
    GIF = auto()
    MESSAGE = auto()


class ScraperConfig:
    def __init__(self):
        self.dump = False
        self.in_dump = False
        self.path = ""
        self.media = ""
        self.caption = ""
        self.caption_url = ""
        self.thumb = None
        self.type = None
        self.success = False

    def set_sauce(self, url):
        self.caption_url = f"\n\n<a href='{url}'>Sauce</a>"

    @classmethod
    async def start(cls, url):
        obj = cls(url=url)
        obj.query_url = url
        obj.set_sauce(url)
        await obj.download_or_extract()
        if obj.success:
            return obj

    def cleanup(self):
        if self.path:
            shutil.rmtree(self.path, ignore_errors=True)
