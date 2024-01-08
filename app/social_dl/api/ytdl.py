import asyncio
import os
import time

import yt_dlp

from app.social_dl.scraper_config import ScraperConfig
from app.utils.media_helper import MediaType
from app.utils.shell import take_ss

# To disable YT-DLP logging
# https://github.com/ytdl-org/youtube-dl/blob/fa7f0effbe4e14fcf70e1dc4496371c9862b64b9/test/helper.py#L92


class FakeLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class YouTubeDL(ScraperConfig):
    def __init__(self, url):
        super().__init__(url=url)
        self.path: str = "downloads/" + str(time.time())
        self.video_path: str = self.path + "/v.mp4"
        self.type = MediaType.VIDEO
        _opts: dict = {
            "outtmpl": self.video_path,
            "ignoreerrors": True,
            "ignore_no_formats_error": True,
            "quiet": True,
            "logger": FakeLogger(),
            "noplaylist": True,
            "format": self.get_format(),
        }
        self.yt_obj: yt_dlp.YoutubeDL = yt_dlp.YoutubeDL(_opts)

    async def download_or_extract(self):
        info: dict = await self.get_info()
        if not info:
            return

        await asyncio.to_thread(self.yt_obj.download, self.raw_url)

        if "youtu" in self.raw_url:
            self.caption: str = (
                f"""__{info.get("channel","")}__:\n**{info.get("title","")}**"""
            )

        if os.path.isfile(self.video_path):
            self.media = self.video_path
            self.thumb = await take_ss(self.video_path, path=self.path)
            self.success = True

    async def get_info(self) -> None | dict:
        if (
            os.path.basename(self.raw_url).startswith("@")
            or "/hashtag/" in self.raw_url
        ):
            return
        info = await asyncio.to_thread(
            self.yt_obj.extract_info, self.raw_url, download=False
        )
        if (
            not info
            or info.get("live_status") == "is_live"
            or info.get("duration", 0) >= 180
        ):
            return
        return info

    def get_format(self) -> str:
        if "/shorts" in self.raw_url:
            return "bv[ext=mp4][res=720]+ba[ext=m4a]/b[ext=mp4]"
        elif "youtu" in self.raw_url:
            return "bv[ext=mp4][res=480]+ba[ext=m4a]/b[ext=mp4]"
        else:
            return "b[ext=mp4]"
