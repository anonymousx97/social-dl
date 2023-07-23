import os
import time
from urllib.parse import urlparse

from app.core import aiohttp_tools, shell
from app.core.scraper_config import ScraperConfig


class Reddit(ScraperConfig):
    def __init__(self, url):
        super().__init__()
        self.set_sauce(url)
        parsed_url = urlparse(url)
        self.url = f"https://www.reddit.com{parsed_url.path}.json?limit=1"

    async def download_or_extract(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_7 rv:5.0; en-US) AppleWebKit/533.31.5 (KHTML, like Gecko) Version/4.0 Safari/533.31.5"
        }
        response = await aiohttp_tools.get_json(url=self.url, headers=headers, json_=True)
        if not response:
            return

        try:
            json_ = response[0]["data"]["children"][0]["data"]
        except BaseException:
            return

        self.caption = f"""__{json_["subreddit_name_prefixed"]}:__\n**{json_["title"]}**"""

        is_vid, is_gallery = json_.get("is_video"), json_.get("is_gallery")

        if is_vid:
            self.path = "downloads/" + str(time.time())
            os.makedirs(self.path)
            self.link = f"{self.path}/v.mp4"
            vid_url = json_["secure_media"]["reddit_video"]["hls_url"]
            await shell.run_shell_cmd(f'ffmpeg -hide_banner -loglevel error -i "{vid_url.strip()}" -c copy {self.link}')
            self.thumb = await shell.take_ss(video=self.link, path=self.path)
            self.video = self.success = True

        elif is_gallery:
            self.link = [val["s"].get("u", val["s"].get("gif")).replace("preview", "i") for val in json_["media_metadata"].values()]
            self.group = self.success = True

        else:
            self.link = json_.get("preview", {}).get("reddit_video_preview", {}).get("fallback_url", json_.get("url_overridden_by_dest", "")).strip()
            if not self.link:
                return
            if self.link.endswith(".gif"):
                self.gif = self.success = True
            else:
                self.photo = self.success = True
