import asyncio
import glob
import os
import time

from app.core import shell
from app.core.scraper_config import MediaType, ScraperConfig


class Gallery_DL(ScraperConfig):
    def __init__(self, url):
        super().__init__()
        self.url = url

    async def download_or_extract(self):
        self.path = "downloads/" + str(time.time())
        os.makedirs(self.path)
        try:
            async with asyncio.timeout(30):
                await shell.run_shell_cmd(
                    f"gallery-dl -q --range '0-4' -D {self.path} '{self.url}'"
                )
        except TimeoutError:
            pass
        files = glob.glob(f"{self.path}/*")
        if not files:
            return self.cleanup()
        self.media = self.success = True
        self.type = MediaType.GROUP
