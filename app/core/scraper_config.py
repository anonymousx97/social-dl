import shutil


class ScraperConfig:
    def __init__(self):
        self.path = ""
        self.link = ""
        self.caption = ""
        self.caption_url = ""
        self.thumb = None
        self.success = False
        self.photo = False
        self.video = False
        self.group = False
        self.gif = False

    def set_sauce(self):
        self.caption_url = f"\n\n<a href='{self.query_url}'>Sauce</a>"

    @classmethod
    async def start(cls, url):
        obj = cls(url=url)
        obj.query_url = url
        obj.set_sauce()
        await obj.download_or_extract()
        if obj.success:
            return obj

    def cleanup(self):
        if self.path:
            shutil.rmtree(self.path, ignore_errors=True)
