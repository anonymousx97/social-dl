import os
from urllib.parse import urlparse

from app import LOGGER, Config, Message, bot
from app.social_dl.scraper_config import ScraperConfig
from app.utils import aiohttp_tools as aio
from app.utils.media_helper import MediaType, get_type


class ApiKeys:
    def __init__(self):
        self.API2_KEYS: list = Config.API_KEYS
        self.api_2 = 0

    # Rotating Key function to avoid hitting limit on single Key
    def get_key(self, func: str) -> str:
        keys = self.API2_KEYS
        count = getattr(self, func) + 1
        if count >= len(keys):
            count = 0
        setattr(self, func, count)
        return keys[count]

    # def switch(self) -> int:
    #     self.switch_val += 1
    #     if self.switch_val >= 3:
    #         self.switch_val = 0
    #     return self.switch_val


api_keys: ApiKeys = ApiKeys()


class Instagram(ScraperConfig):
    def __init__(self, url):
        self.APIS = (
            "check_dump",
            "no_api_dl",
            "api_2",
        )

        super().__init__(url=url)
        parsed_url = urlparse(url)
        self.shortcode: str = os.path.basename(parsed_url.path.rstrip("/"))
        self.api_url = f"https://www.instagram.com/graphql/query?query_hash=2b0673e0dc4580674a88d426fe00ea90&variables=%7B%22shortcode%22%3A%22{self.shortcode}%22%7D"
        self.dump: bool = True

    async def check_dump(self) -> None | bool:
        if not Config.DUMP_ID:
            return
        async for message in bot.search_messages(Config.DUMP_ID, "#" + self.shortcode):
            self.media: Message = message
            self.type: MediaType = MediaType.MESSAGE
            self.in_dump: bool = True
            return True

    async def download_or_extract(self) -> None:
        for api in self.APIS:
            func = getattr(self, api)
            if await func():
                self.success: bool = True
                break

    async def no_api_dl(self):
        response: dict | None = await aio.get_json(url=self.api_url)
        if (
            not response
            or "data" not in response
            or not response["data"]["shortcode_media"]
        ):
            LOGGER.error(response)
            return
        return await self.parse_ghraphql(response["data"]["shortcode_media"])

    async def api_2(self) -> bool | None:
        if not Config.API_KEYS:
            return
        # "/?__a=1&__d=1"
        response: dict | None = await aio.get_json(
            url="https://api.webscraping.ai/html",
            timeout=30,
            params={
                "api_key": api_keys.get_key("api_2"),
                "url": self.api_url,
                "proxy": "residential",
                "js": "false",
            },
        )
        if (
            not response
            or "data" not in response.keys()
            or not response["data"]["shortcode_media"]
        ):
            LOGGER.error(response)
            return
        self.caption = ".."
        return await self.parse_ghraphql(response["data"]["shortcode_media"])

    async def parse_ghraphql(self, json_: dict) -> str | list | None:
        type_check: str | None = json_.get("__typename", None)
        if not type_check:
            return
        elif type_check == "GraphSidecar":
            self.media: list[str] = [
                i["node"].get("video_url") or i["node"].get("display_url")
                for i in json_["edge_sidecar_to_children"]["edges"]
            ]
            self.type: MediaType = MediaType.GROUP
        else:
            self.media: str = json_.get("video_url", json_.get("display_url"))
            self.thumb: str = json_.get("display_url")
            self.type: MediaType = get_type(self.media)
        return self.media

    async def parse_v2_json(self, data: dict):
        if data.get("carousel_media"):
            self.media = []
            for media in data["carousel_media"]:
                if media.get("video_dash_manifest"):
                    self.media.append(media["video_versions"][0]["url"])
                else:
                    self.media.append(media["image_versions2"]["candidates"][0]["url"])
            self.type = MediaType.GROUP
        elif data.get("video_dash_manifest"):
            self.media = data["video_versions"][0]["url"]
            self.type = MediaType.VIDEO
        else:
            self.media = data["image_versions2"]["candidates"][0]["url"]
            self.type = MediaType.PHOTO
        return 1
