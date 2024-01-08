import asyncio
import glob
import shutil
from time import time
from urllib.parse import urlparse

import yt_dlp

from app import Message, bot
from app.social_dl.api.ytdl import FakeLogger
from app.utils.aiohttp_tools import in_memory_dl

domains = [
    "www.youtube.com",
    "youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtube-nocookie.com",
    "music.youtube.com",
]


@bot.add_cmd(cmd="song")
async def song_dl(bot: bot, message: Message) -> None | Message:
    reply_query = None
    for link in message.reply_text_list:
        if urlparse(link).netloc in domains:
            reply_query = link
            break
    query = reply_query or message.flt_input
    if not query:
        return await message.reply("Give a song name or link to download.")
    response: Message = await message.reply("Searching....")
    dl_path: str = f"downloads/{time()}/"
    query_or_search: str = query if query.startswith("http") else f"ytsearch:{query}"
    if "-m" in message.flags:
        a_format = "mp3"
    else:
        a_format = "opus"
    yt_opts = {
        "logger": FakeLogger(),
        "outtmpl": dl_path + "%(title)s.%(ext)s",
        "format": "bestaudio",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": a_format},
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ],
    }
    ytdl: yt_dlp.YoutubeDL = yt_dlp.YoutubeDL(yt_opts)
    yt_info: dict = await asyncio.to_thread(ytdl.extract_info, query_or_search)
    if not query_or_search.startswith("http"):
        yt_info: str = yt_info["entries"][0]
    duration: int = yt_info["duration"]
    artist: str = yt_info["channel"]
    thumb = await in_memory_dl(yt_info["thumbnail"])
    down_path: list = glob.glob(dl_path + "*")
    if not down_path:
        return await response.edit("Not found")
    await response.edit("Uploading....")
    for audio_file in down_path:
        if audio_file.endswith((".opus", ".mp3")):
            await message.reply_audio(
                audio=audio_file,
                duration=int(duration),
                performer=str(artist),
                thumb=thumb,
            )
    await response.delete()
    shutil.rmtree(dl_path, ignore_errors=True)
