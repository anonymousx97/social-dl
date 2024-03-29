import os
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.social_dl.scraper_config import ScraperConfig
from app.utils import aiohttp_tools
from app.utils.media_helper import MediaType


class Threads(ScraperConfig):
    def __init__(self, url):
        super().__init__(url=url)

    async def download_or_extract(self):
        shortcode: str = os.path.basename(urlparse(self.raw_url).path.rstrip("/"))

        response: str = await (
            await aiohttp_tools.SESSION.get(
                f"https://www.threads.net/t/{shortcode}/embed/"
            )
        ).text()

        soup = BeautifulSoup(response, "html.parser")

        if div := soup.find("div", {"class": "SingleInnerMediaContainer"}):
            if video := div.find("video"):
                self.media = video.find("source").get("src")
                self.success = True
                self.type = MediaType.VIDEO

            elif image := div.find("img", {"class": "img"}):
                self.media = image.get("src")
                self.success = True
                self.type = MediaType.PHOTO
