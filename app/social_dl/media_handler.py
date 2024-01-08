import asyncio
import glob
import json
import os
import traceback
from functools import lru_cache
from io import BytesIO
from urllib.parse import urlparse

from pyrogram.enums import ChatType
from pyrogram.errors import (
    MediaEmpty,
    PhotoSaveFileInvalid,
    WebpageCurlFailed,
    WebpageMediaEmpty,
)
from pyrogram.types import InputMediaPhoto, InputMediaVideo

from app import Config, bot
from app.core import Message
from app.social_dl.api.gallery_dl import GalleryDL
from app.social_dl.api.instagram import Instagram
from app.social_dl.api.reddit import Reddit
from app.social_dl.api.threads import Threads

from app.social_dl.api.tiktok import Tiktok
from app.social_dl.api.ytdl import YouTubeDL
from app.utils import aiohttp_tools, shell
from app.utils.media_helper import MediaExts, MediaType

url_map: dict = {
    "tiktok.com": Tiktok,
    "www.instagram.com": Instagram,
    "www.reddit.com": Reddit,
    "reddit.com": Reddit,
    "www.threads.net": Threads,
    "twitter.com": GalleryDL,
    "x.com": GalleryDL,
    "www.x.com": GalleryDL,
    "youtube.com": YouTubeDL,
    "youtu.be": YouTubeDL,
    "www.facebook.com": YouTubeDL,
}


@lru_cache()
def get_url_dict_items():
    return url_map.items()


class MediaHandler:
    def __init__(self, message: Message) -> None:
        self.exceptions = []
        self.media_objects: list[
            Tiktok | Instagram | Reddit | Threads | GalleryDL | YouTubeDL
        ] = []
        self.sender_dict = {}
        self.message: Message = message
        self.doc: bool = "-d" in message.flags
        self.spoiler: bool = "-s" in message.flags
        self.args_: dict = {
            "chat_id": self.message.chat.id,
            "reply_to_message_id": message.reply_id,
        }

    def __str__(self):
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False)

    def get_sender(self, reply: bool = False) -> str:
        if "-ns" in self.message.flags:
            return ""
        text: str = f"\nShared by : "
        if self.message.chat.type == ChatType.CHANNEL:
            author: str | None = self.message.author_signature
            return text + author if author else ""
        elif reply and self.message.replied and self.message.replied.from_user:
            return text + self.message.from_user.first_name
        elif self.message.from_user.first_name:
            return text + self.message.from_user.first_name or ""
        else:
            return ""

    async def get_media(self) -> None:
        tasks: list[asyncio.Task] = []
        for link in self.message.text_list + self.message.reply_text_list:
            if "music.youtube.com" in link:
                continue
            if match := url_map.get(urlparse(link).netloc):
                tasks.append(asyncio.create_task(match.start(link)))
                self.sender_dict[link] = self.get_sender(
                    reply=link in self.message.reply_text_list
                )
                continue
            for key, val in get_url_dict_items():
                if key in link:
                    tasks.append(asyncio.create_task(val.start(link)))
                    self.sender_dict[link] = self.get_sender(
                        reply=link in self.message.reply_text_list
                    )
        self.media_objects = [task for task in await asyncio.gather(*tasks) if task]

    async def send_media(self) -> None:
        for obj in self.media_objects:
            if "-nc" in self.message.flags:
                caption = ""
            else:
                caption = obj.caption + obj.sauce + self.sender_dict[obj.raw_url]
            try:
                if self.doc and not obj.in_dump:
                    await self.send_document(obj.media, caption=caption, path=obj.path)
                    continue
                elif obj.type == MediaType.GROUP:
                    await self.send_group(obj, caption=caption)
                    continue
                elif obj.type == MediaType.MESSAGE:
                    await obj.media.copy(self.message.chat.id, caption=caption)
                    continue
                post: Message = await self.send(
                    *await obj.get_coro(**self.args_), caption=caption
                )
                if obj.dump and Config.DUMP_ID:
                    caption = f"#{obj.shortcode}\n{self.sender_dict[obj.raw_url]}\nChat:{self.message.chat.title}\nID:{self.message.chat.id}"
                    await post.copy(Config.DUMP_ID, caption=caption)
            except BaseException:
                self.exceptions.append("\n".join([obj.raw_url, traceback.format_exc()]))

    async def send(self, coro, kwargs: dict, type: str, caption: str) -> Message:
        try:
            try:
                post: Message = await coro(
                    **kwargs, caption=caption, has_spoiler=self.spoiler
                )
            except (MediaEmpty, WebpageCurlFailed, WebpageMediaEmpty):
                kwargs[type] = await aiohttp_tools.in_memory_dl(kwargs[type])
                post: Message = await coro(
                    **kwargs, caption=caption, has_spoiler=self.spoiler
                )
        except PhotoSaveFileInvalid:
            post: Message = await bot.send_document(
                **self.args_,
                document=kwargs[type],
                caption=caption,
                force_document=True,
            )
        return post

    async def send_document(self, docs: list, caption: str, path="") -> None:
        if not path:
            if not isinstance(docs, list):
                docs = [docs]
            docs = await asyncio.gather(
                *[aiohttp_tools.in_memory_dl(doc) for doc in docs]
            )
        else:
            docs = glob.glob(f"{path}/*")
        for doc in docs:
            await bot.send_document(
                **self.args_, document=doc, caption=caption, force_document=True
            )
            await asyncio.sleep(0.5)

    async def send_group(self, media_obj, caption: str) -> None:
        if media_obj.path:
            sorted: dict = await sort_local_media(media_obj.path)
        else:
            sorted: dict = await sort_url_media(media_obj.media)

        sorted_group: list[
            str, list[InputMediaVideo | InputMediaPhoto]
        ] = await sort_group(media_dict=sorted, caption=caption, spoiler=self.spoiler)
        for data in sorted_group:
            if isinstance(data, list):
                await bot.send_media_group(**self.args_, media=data)
            else:
                await self.send(
                    coro=bot.send_animation,
                    kwargs=dict(animation=data, unsave=True),
                    caption=caption,
                    type="animation",
                )
            await asyncio.sleep(1)

    @classmethod
    async def process(cls, message):
        obj = cls(message=message)
        await obj.get_media()
        await obj.send_media()
        [m_obj.cleanup() for m_obj in obj.media_objects]
        return obj


async def sort_local_media(path: str):
    [os.rename(file_, file_ + ".png") for file_ in glob.glob(f"{path}/*.webp")]
    return {file: file for file in glob.glob(f"{path}/*")}


async def sort_url_media(urls: list):
    media: tuple[BytesIO] = await asyncio.gather(
        *[aiohttp_tools.in_memory_dl(url) for url in urls]
    )
    return {file_obj.name: file_obj for file_obj in media}


async def sort_group(
    media_dict: dict,
    caption="",
    spoiler=False,
) -> list[str, list[InputMediaVideo | InputMediaPhoto]]:
    images, videos, animations = [], [], []
    for file_name, file in media_dict.items():
        name, ext = os.path.splitext(file_name.lower())
        if ext in MediaExts.PHOTO:
            images.append(InputMediaPhoto(file, caption=caption, has_spoiler=spoiler))
        elif ext in MediaExts.VIDEO:
            if isinstance(file, BytesIO):
                videos.append(
                    InputMediaVideo(file, caption=caption, has_spoiler=spoiler)
                )
            elif not await shell.check_audio(file):
                animations.append(file)
            else:
                videos.append(
                    InputMediaVideo(file, caption=caption, has_spoiler=spoiler)
                )
        elif ext in MediaExts.GIF:
            animations.append(file)
    chunk_imgs = [images[imgs : imgs + 5] for imgs in range(0, len(images), 5)]
    chunk_vids = [videos[vids : vids + 5] for vids in range(0, len(videos), 5)]
    return [*chunk_imgs, *chunk_vids, *animations]
