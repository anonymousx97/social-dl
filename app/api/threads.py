import os
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.core import aiohttp_tools
from app.core.scraper_config import ScraperConfig


class Threads(ScraperConfig):
    def __init__(self, url):
        super().__init__()
        self.url = url

    async def download_or_extract(self):
        shortcode = os.path.basename(urlparse(self.url).path.rstrip("/"))

        response = await (
            await aiohttp_tools.SESSION.get(
                f"https://www.threads.net/t/{shortcode}/embed/"
            )
        ).text()

        soup = BeautifulSoup(response, "html.parser")

        if div := soup.find("div", {"class": "SingleInnerMediaContainer"}):
            if video := div.find("video"):
                self.link = video.find("source").get("src")
                self.video = self.success = True

            elif image := div.find("img", {"class": "img"}):
                self.link = image.get("src")
                self.photo = self.success = True
