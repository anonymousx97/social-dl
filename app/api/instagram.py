import os
from urllib.parse import urlparse

from app import Config
from app.core import aiohttp_tools
from app.core.scraper_config import ScraperConfig

API_KEYS = { "KEYS": Config.API_KEYS , "counter": 0 }

class Instagram(ScraperConfig):
    def __init__(self, url):
        super().__init__()
        shortcode = os.path.basename(urlparse(url).path.rstrip("/"))
        self.url = (
            f"https://www.instagram.com/graphql/query?query_hash=2b0673e0dc4580674a88d426fe00ea90&variables=%7B%22shortcode%22%3A%22{shortcode}%22%7D"
        )
        self.set_sauce(url)

    async def download_or_extract(self):
        for func in [self.no_api_dl, self.api_dl]:
            if await func():
                self.success = True
                break

    async def no_api_dl(self):
        response = await aiohttp_tools.get_json(url=self.url)
        if not response or "data" not in response or not response["data"]["shortcode_media"]:
            return
        return await self.parse_ghraphql(response["data"]["shortcode_media"])


    async def api_dl(self):
        param = {"api_key": await self.get_key(), "url": self.url, "proxy": "residential", "js": False}
        response = await aiohttp_tools.get_json(url="https://api.webscraping.ai/html", timeout=30, params=param)
        if not response or "data" not in response or not response["data"]["shortcode_media"]:
            return
        self.caption = ".."
        return await self.parse_ghraphql(response["data"]["shortcode_media"])

    async def parse_ghraphql(self, json_: dict):
        type_check = json_.get("__typename", None)
        if not type_check:
            return
        elif type_check == "GraphSidecar":
            self.link = [i["node"].get("video_url") or i["node"].get("display_url") for i in json_["edge_sidecar_to_children"]["edges"]]
            self.group = True
        else:
            if link := json_.get("video_url"):
                self.link = link
                self.thumb = json_.get("display_url")
                self.video = True
            else:
                self.link = json_.get("display_url")
                self.photo = True
        return self.link

    # Rotating Key function to avoid hitting limit on single Key
    async def get_key(self):
        keys, count = API_KEYS
        count += 1
        if count == len(keys):
            count = 0
        ret_key = keys[count]
        API_KEYS["counter"] = count
        return ret_key
