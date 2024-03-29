import asyncio
import glob
import os
import time

from app.social_dl.scraper_config import ScraperConfig
from app.utils import shell
from app.utils.media_helper import MediaType


class GalleryDL(ScraperConfig):
    def __init__(self, url: str):
        super().__init__(url=url)

    async def download_or_extract(self):
        self.path: str = "downloads/" + str(time.time())
        os.makedirs(self.path)
        try:
            async with asyncio.timeout(30):
                await shell.run_shell_cmd(
                    f"gallery-dl -q --range '0-4' -D {self.path} '{self.raw_url}'"
                )
        except TimeoutError:
            pass
        files: list[str] = glob.glob(f"{self.path}/*")
        if not files:
            return self.cleanup()
        self.media = self.success = True
        self.type: MediaType = MediaType.GROUP
