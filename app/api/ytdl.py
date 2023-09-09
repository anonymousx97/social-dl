import asyncio
import os
import time

import yt_dlp

from app.core.scraper_config import MediaType, ScraperConfig
from app.core.shell import take_ss


# To disable YT-DLP logging
# https://github.com/ytdl-org/youtube-dl/blob/fa7f0effbe4e14fcf70e1dc4496371c9862b64b9/test/helper.py#L92
class FakeLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class YT_DL(ScraperConfig):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.path = "downloads/" + str(time.time())
        self.video_path = self.path + "/v.mp4"
        self.type = MediaType.VIDEO
        _opts = {
            "outtmpl": self.video_path,
            "ignoreerrors": True,
            "ignore_no_formats_error": True,
            "quiet": True,
            "logger": FakeLogger(),
            "noplaylist": True,
            "format": self.get_format(),
        }
        self.yt_obj = yt_dlp.YoutubeDL(_opts)

    async def download_or_extract(self):
        info = await self.get_info()
        if not info:
            return

        await asyncio.to_thread(self.yt_obj.download, self.url)

        if "youtu" in self.url:
            self.caption = (
                f"""__{info.get("channel","")}__:\n**{info.get("title","")}**"""
            )

        if os.path.isfile(self.video_path):
            self.media = self.video_path
            self.thumb = await take_ss(self.video_path, path=self.path)
            self.success = True

    async def get_info(self):
        if os.path.basename(self.url).startswith("@") or "/hashtag/" in self.url:
            return
        info = await asyncio.to_thread(
            self.yt_obj.extract_info, self.url, download=False
        )
        if (
            not info
            or info.get("live_status") == "is_live"
            or info.get("duration", 0) >= 180
        ):
            return
        return info

    def get_format(self):
        if "/shorts" in self.url:
            return "bv[ext=mp4][res=720]+ba[ext=m4a]/b[ext=mp4]"
        elif "youtu" in self.url:
            return "bv[ext=mp4][res=480]+ba[ext=m4a]/b[ext=mp4]"
        else:
            return "b[ext=mp4]"
