import asyncio
import glob
import os
import traceback
from urllib.parse import urlparse

from pyrogram.errors import MediaEmpty, PhotoSaveFileInvalid, WebpageCurlFailed
from pyrogram.types import InputMediaPhoto, InputMediaVideo

from app import Config
from app.api.gallerydl import Gallery_DL
from app.api.instagram import Instagram
from app.api.reddit import Reddit
from app.api.threads import Threads
from app.api.tiktok import Tiktok
from app.api.ytdl import YT_DL
from app.core import aiohttp_tools, shell
from app.core.scraper_config import MediaType

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


class MediaHandler:
    def __init__(self, message):
        self.exceptions, self.media_objects, self.sender_dict = [], [], {}
        self.__client = message._client
        self.message = message
        self.doc = "-d" in message.flags
        self.spoiler = "-s" in message.flags
        self.args_ = {
            "chat_id": self.message.chat.id,
            "reply_to_message_id": message.reply_id,
        }

    def get_sender(self, reply=False):
        if "-ns" in self.message.flags:
            return ""
        text = f"\nShared by : "
        author = self.message.author_signature
        sender = user.first_name if (user := self.message.from_user) else ""
        reply_sender = ""
        if reply:
            reply_msg = self.message.replied
            reply_sender = (
                reply_user.first_name if (reply_user := reply_msg.from_user) else ""
            )
        if any((author, sender, reply_sender)):
            return text + (author or sender if not reply else reply_sender)
        else:
            return ""

    async def get_media(self):
        async with asyncio.TaskGroup() as task_group:
            tasks = []
            text_list = self.message.text_list
            reply_text_list = self.message.reply_text_list
            for link in text_list + reply_text_list:
                reply = link in reply_text_list
                if match := url_map.get(urlparse(link).netloc):
                    tasks.append(task_group.create_task(match.start(link)))
                    self.sender_dict[link] = self.get_sender(reply=reply)
                else:
                    for key, val in url_map.items():
                        if key in link:
                            tasks.append(task_group.create_task(val.start(link)))
                            self.sender_dict[link] = self.get_sender(reply=reply)
        self.media_objects = [task.result() for task in tasks if task.result()]

    async def send_media(self):
        for obj in self.media_objects:
            if "-nc" in self.message.flags:
                caption = ""
            else:
                caption = (
                    obj.caption + obj.caption_url + self.sender_dict[obj.query_url]
                )
            try:
                if self.doc and not obj.in_dump:
                    await self.send_document(obj.media, caption=caption, path=obj.path)
                    continue
                match obj.type:
                    case MediaType.MESSAGE:
                        await obj.media.copy(self.message.chat.id, caption=caption)
                        continue
                    case MediaType.GROUP:
                        await self.send_group(obj, caption=caption)
                        continue
                    case MediaType.PHOTO:
                        post = await self.send(
                            media={"photo": obj.media},
                            method=self.__client.send_photo,
                            caption=caption,
                        )
                    case MediaType.VIDEO:
                        post = await self.send(
                            media={"video": obj.media},
                            method=self.__client.send_video,
                            thumb=await aiohttp_tools.thumb_dl(obj.thumb),
                            caption=caption,
                        )
                    case MediaType.GIF:
                        post = await self.send(
                            media={"animation": obj.media},
                            method=self.__client.send_animation,
                            caption=caption,
                            unsave=True,
                        )
                if obj.dump and Config.DUMP_ID:
                    await post.copy(Config.DUMP_ID, caption="#" + obj.shortcode)
            except BaseException:
                self.exceptions.append(
                    "\n".join([obj.caption_url.strip(), traceback.format_exc()])
                )

    async def send(self, media, method, **kwargs):
        try:
            try:
                post = await method(
                    **media, **self.args_, **kwargs, has_spoiler=self.spoiler
                )
            except (MediaEmpty, WebpageCurlFailed):
                key, value = list(media.items())[0]
                media[key] = await aiohttp_tools.in_memory_dl(value)
                post = await method(
                    **media, **self.args_, **kwargs, has_spoiler=self.spoiler
                )
        except PhotoSaveFileInvalid:
            post = await self.__client.send_document(
                **self.args_, document=media, caption=caption, force_document=True
            )
        return post

    async def send_document(self, docs, caption, path=""):
        if not path:
            docs = await asyncio.gather(
                *[aiohttp_tools.in_memory_dl(doc) for doc in docs]
            )
        else:
            [os.rename(file_, file_ + ".png") for file_ in glob.glob(f"{path}/*.webp")]
            docs = glob.glob(f"{path}/*")
        for doc in docs:
            await self.__client.send_document(
                **self.args_, document=doc, caption=caption, force_document=True
            )
            await asyncio.sleep(0.5)

    async def send_group(self, media_obj, caption):
        sorted = await sort_media(
            caption=caption,
            spoiler=self.spoiler,
            urls=media_obj.media,
            path=media_obj.path,
        )
        for data in sorted:
            if isinstance(data, list):
                await self.__client.send_media_group(**self.args_, media=data)
            else:
                await self.send(
                    media={"animation": data},
                    method=self.__client.send_animation,
                    caption=caption,
                    unsave=True,
                )
            await asyncio.sleep(1)

    @classmethod
    async def process(cls, message):
        obj = cls(message=message)
        await obj.get_media()
        await obj.send_media()
        [m_obj.cleanup() for m_obj in obj.media_objects]
        return obj


async def sort_media(caption="", spoiler=False, urls=None, path=None):
    images, videos, animations = [], [], []
    if path and os.path.exists(path):
        [os.rename(file_, file_ + ".png") for file_ in glob.glob(f"{path}/*.webp")]
        media = glob.glob(f"{path}/*")
    else:
        media = await asyncio.gather(*[aiohttp_tools.in_memory_dl(url) for url in urls])
    for file in media:
        if path:
            name = file.lower()
        else:
            name = file.name.lower()
        if name.endswith((".png", ".jpg", ".jpeg")):
            images.append(InputMediaPhoto(file, caption=caption, has_spoiler=spoiler))
        elif name.endswith((".mp4", ".mkv", ".webm")):
            if not urls and not await shell.check_audio(file):
                animations.append(file)
            else:
                videos.append(
                    InputMediaVideo(file, caption=caption, has_spoiler=spoiler)
                )
        elif name.endswith(".gif"):
            animations.append(file)
    return await make_chunks(images, videos, animations)


async def make_chunks(images=[], videos=[], animations=[]):
    chunk_imgs = [images[imgs : imgs + 5] for imgs in range(0, len(images), 5)]
    chunk_vids = [videos[vids : vids + 5] for vids in range(0, len(videos), 5)]
    return [*chunk_imgs, *chunk_vids, *animations]
