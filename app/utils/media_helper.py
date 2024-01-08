from enum import Enum, auto
from os.path import basename, splitext
from urllib.parse import urlparse

from pyrogram.enums import MessageMediaType
from pyrogram.types import Message


class MediaType(Enum):
    AUDIO = auto()
    DOCUMENT = auto()
    GIF = auto()
    GROUP = auto()
    MESSAGE = auto()
    PHOTO = auto()
    STICKER = auto()
    VIDEO = auto()


class MediaExts:
    PHOTO = {".png", ".jpg", ".jpeg", ".heic", ".webp"}
    VIDEO = {".mp4", ".mkv", ".webm"}
    GIF = {".gif"}
    AUDIO = {".aac", ".mp3", ".opus", ".m4a", ".ogg", ".flac"}


def bytes_to_mb(size: int):
    return round(size / 1048576, 1)


def get_filename(url: str) -> str:
    name = basename(urlparse(url).path.rstrip("/"))
    if name.lower().endswith((".webp", ".heic")):
        name = name + ".jpg"
    elif name.lower().endswith(".webm"):
        name = name + ".mp4"
    return name


def get_type(url: str | None = "", path: str | None = "") -> MediaType | None:
    if url:
        media = get_filename(url)
    else:
        media = path
    name, ext = splitext(media)
    if ext in MediaExts.PHOTO:
        return MediaType.PHOTO
    if ext in MediaExts.VIDEO:
        return MediaType.VIDEO
    if ext in MediaExts.GIF:
        return MediaType.GIF
    if ext in MediaExts.AUDIO:
        return MediaType.AUDIO
    return MediaType.DOCUMENT


def get_tg_media_details(message: Message):
    match message.media:
        case MessageMediaType.PHOTO:
            file = message.photo
            file.file_name = "photo.jpg"
            return file
        case MessageMediaType.AUDIO:
            return message.audio
        case MessageMediaType.ANIMATION:
            return message.animation
        case MessageMediaType.DOCUMENT:
            return message.document
        case MessageMediaType.STICKER:
            return message.sticker
        case MessageMediaType.VIDEO:
            return message.video
        case MessageMediaType.VOICE:
            return message.voice
        case _:
            return
