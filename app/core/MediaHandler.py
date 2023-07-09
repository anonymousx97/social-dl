import asyncio
import glob
import os
import traceback
from urllib.parse import urlparse

from pyrogram.errors import MediaEmpty, PhotoSaveFileInvalid, WebpageCurlFailed
from pyrogram.types import InputMediaPhoto, InputMediaVideo

from app.api.gallerydl import Gallery_DL
from app.api.instagram import Instagram
from app.api.reddit import Reddit
from app.api.threads import Threads
from app.api.tiktok import Tiktok
from app.api.ytdl import YT_DL
from app.core import aiohttp_tools, shell

# Thanks Jeel Patel for the concept TG[@jeelpatel231]

url_map = {
    "tiktok.com": Tiktok,
    "www.instagram.com": Instagram,
    "www.reddit.com": Reddit,
    "reddit.com": Reddit,
    "www.threads.net": Threads,
    "twitter.com": Gallery_DL,
    "youtube.com": YT_DL,
    "youtu.be": YT_DL,
    "www.facebook.com": YT_DL,
}


class ExtractAndSendMedia:
    def __init__(self, message):
        self.exceptions, self.media_objects = [], []
        self.message = message
        self.doc = "-d" in message.flags
        self.spoiler = "-s" in message.flags
        self.sender = "" if "-ns" in message.flags else f"\nShared by : {self.extract_sender()}"
        self.args_ = {"chat_id": self.message.chat.id, "reply_to_message_id": message.reply_id}

    def extract_sender(self):
        author = self.message.author_signature
        sender = user.first_name if (user := self.message.from_user) else ""
        return author or sender

    async def get_media(self):
        async with asyncio.TaskGroup() as task_group:
            tasks = []
            for link in self.message.get_text_list:
                if match := url_map.get(urlparse(link).netloc):
                    tasks.append(task_group.create_task(match.start(link)))
                else:
                    for key, val in url_map.items():
                        if key in link:
                            tasks.append(task_group.create_task(val.start(link)))
        self.media_objects = [task.result() for task in tasks if task.result()]

    async def send_media(self):
        for obj in self.media_objects:
            if "-nc" in self.message.flags:
                caption = ""
            else:
                caption = obj.caption + obj.caption_url + self.sender
            try:
                if self.doc:
                    await self.send_document(obj.link, caption=caption, path=obj.path)
                elif obj.group:
                    await self.send_group(obj, caption=caption)
                elif obj.photo:
                    await self.send_photo(obj.link, caption=caption)
                elif obj.video:
                    await self.send_video(obj.link, thumb=obj.thumb, caption=caption)
                elif obj.gif:
                    await self.send_animation(obj.link, caption=caption)
            except BaseException:
                self.exceptions.append(traceback.format_exc())

    async def send_photo(self, photo, caption):
        try:
            try:
                await self.message._client.send_photo(**self.args_, photo=photo, caption=caption, has_spoiler=self.spoiler)
            except (MediaEmpty, WebpageCurlFailed):
                photo = await aiohttp_tools.in_memory_dl(photo)
                await self.message._client.send_photo(**self.args_, photo=photo, caption=caption, has_spoiler=self.spoiler)
        except PhotoSaveFileInvalid:
            await self.message._client.send_document(**self.args, document=photo, caption=caption, force_document=True)

    async def send_video(self, video, caption, thumb):
        try:
            await self.message._client.send_video(
                **self.args_, video=video, caption=caption, thumb=await aiohttp_tools.thumb_dl(thumb), has_spoiler=self.spoiler
            )
        except (MediaEmpty, WebpageCurlFailed):
            video = await aiohttp_tools.in_memory_dl(video)
            await self.message._client.send_video(
                **self.args_, video=video, caption=caption, thumb=await aiohttp_tools.thumb_dl(thumb), has_spoiler=self.spoiler
            )

    async def send_animation(self, gif, caption):
        try:
            await self.message._client.send_animation(**self.args_, animation=gif, caption=caption, unsave=True, has_spoiler=self.spoiler)
        except (MediaEmpty, WebpageCurlFailed):
            gif = await aiohttp_tools.in_memory_dl(gif)
            await self.message._client.send_animation(**self.args_, animation=gif, caption=caption, unsave=True, has_spoiler=self.spoiler)

    async def send_document(self, docs, caption, path=""):
        if not path:
            docs = await asyncio.gather(*[aiohttp_tools.in_memory_dl(doc) for doc in docs])
        else:
            [os.rename(file_, file_ + ".png") for file_ in glob.glob(f"{path}/*.webp")]
            docs = glob.glob(f"{path}/*")
        for doc in docs:
            try:
                await self.message._client.send_document(**self.args_, document=doc, caption=caption, force_document=True)
            except (MediaEmpty, WebpageCurlFailed):
                doc = await aiohttp_tools.in_memory_dl(doc)
                await self.message._client.send_document(**self.args_, document=doc, caption=caption, force_document=True)
            await asyncio.sleep(0.5)

    async def send_group(self, media, caption):
        if media.path:
            sorted = await self.sort_media_path(media.path, caption)
        else:
            sorted = await self.sort_media_urls(media.link, caption)
        for data in sorted:
            if isinstance(data, list):
                await self.message._client.send_media_group(**self.args_, media=data)
            else:
                await self.send_animation(data, caption=caption)
            await asyncio.sleep(1)

    async def sort_media_path(self, path, caption):
        [os.rename(file_, file_ + ".png") for file_ in glob.glob(f"{path}/*.webp")]
        images, videos, animations = [], [], []
        for file in glob.glob(f"{path}/*"):
            if file.endswith((".png", ".jpg", ".jpeg")):
                images.append(InputMediaPhoto(file, caption=caption, has_spoiler=self.spoiler))
            if file.endswith((".mp4", ".mkv", ".webm")):
                has_audio = await shell.check_audio(file)
                if not has_audio:
                    animations.append(file)
                else:
                    videos.append(InputMediaVideo(file, caption=caption, has_spoiler=self.spoiler))
        return await self.make_chunks(images, videos, animations)

    async def sort_media_urls(self, urls, caption):
        images, videos, animations = [], [], []
        downloads = await asyncio.gather(*[aiohttp_tools.in_memory_dl(url) for url in urls])
        for file_obj in downloads:
            if file_obj.name.endswith((".png", ".jpg", ".jpeg")):
                images.append(InputMediaPhoto(file_obj, caption=caption, has_spoiler=self.spoiler))
            if file_obj.name.endswith((".mp4", ".mkv", ".webm")):
                videos.append(InputMediaVideo(file_obj, caption=caption, has_spoiler=self.spoiler))
            if file_obj.name.endswith(".gif"):
                animations.append(file_obj)
        return await self.make_chunks(images, videos, animations)

    async def make_chunks(self, images=[], videos=[], animations=[]):
        chunk_imgs = [images[imgs : imgs + 5] for imgs in range(0, len(images), 5)]
        chunk_vids = [videos[vids : vids + 5] for vids in range(0, len(videos), 5)]
        return [*chunk_imgs, *chunk_vids, *animations]

    @classmethod
    async def process(cls, message):
        obj = cls(message=message)
        await obj.get_media()
        await obj.send_media()
        [m_obj.cleanup() for m_obj in obj.media_objects]
        return obj
