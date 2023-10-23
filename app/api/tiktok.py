from app.api.tiktok_scraper import Scraper as Tiktok_Scraper
from app.core.scraper_config import MediaType, ScraperConfig

tiktok_scraper = Tiktok_Scraper(quiet=True)


class Tiktok(ScraperConfig):
    def __init__(self, url):
        super().__init__()
        self.url: str = url

    async def download_or_extract(self):
        media: dict | None = await tiktok_scraper.hybrid_parsing(self.url)
        if not media or "status" not in media or media["status"] == "failed":
            return
        if "video_data" in media:
            self.media: str = media["video_data"]["nwm_video_url_HQ"]
            self.thumb: str = media["cover_data"]["dynamic_cover"]["url_list"][0]
            self.success = True
            self.type = MediaType.VIDEO
        if "image_data" in media:
            self.media: list[str] = media["image_data"]["no_watermark_image_list"]
            self.success = True
            self.type = MediaType.GROUP
