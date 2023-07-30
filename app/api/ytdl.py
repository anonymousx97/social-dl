import asyncio
import os
import time

import yt_dlp

from app.core.scraper_config import ScraperConfig
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
        self._opts = {
            "outtmpl": self.video_path,
            "ignoreerrors": True,
            "ignore_no_formats_error": True,
            "quiet": True,
            "logger": FakeLogger(),
            "noplaylist": True,
        }
        self.set_format()

    async def download_or_extract(self):
        if self.check_url():
            return
        with yt_dlp.YoutubeDL(self._opts) as yt_obj:
            info = await asyncio.to_thread(
                yt_obj.extract_info, self.url, download=False
            )

            if not info or info.get("duration", 0) >= 300:
                return

            await asyncio.to_thread(yt_obj.download, self.url)

            if "youtu" in self.url:
                self.caption = (
                    f"""__{info.get("channel","")}__:\n**{info.get("title","")}**"""
                )

        if os.path.isfile(self.video_path):
            self.link = self.video_path
            self.thumb = await take_ss(self.video_path, path=self.path)
            self.video = self.success = True

    def check_url(self):
        if "youtu" in self.url and (
            "/live" in self.url or os.path.basename(self.url).startswith("@")
        ):
            return 1

    def set_format(self):
        if "/shorts" in self.url:
            self._opts["format"] = "bv[ext=mp4][res=720]+ba[ext=m4a]/b[ext=mp4]"
        elif "youtu" in self.url:
            self._opts["format"] = "bv[ext=mp4][res=480]+ba[ext=m4a]/b[ext=mp4]"
        else:
            self._opts["format"] = "b[ext=mp4]"
