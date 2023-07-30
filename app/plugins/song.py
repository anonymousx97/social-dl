import asyncio
import glob
import shutil
from time import time
from urllib.parse import urlparse

import yt_dlp

from app import bot
from app.api.ytdl import FakeLogger
from app.core.aiohttp_tools import in_memory_dl

domains = [
    "www.youtube.com",
    "youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtube-nocookie.com",
    "music.youtube.com",
]


@bot.add_cmd(cmd="song")
async def song_dl(bot, message):
    reply_query = None
    audio_file = None
    artist = None
    if message.replied:
        for link in message.replied.text.split():
            if urlparse(link).netloc in domains:
                reply_query = link
                break
    query = reply_query or message.flt_input
    if not query:
        return await message.reply("Give a song name or link to download.")
    response = await message.reply("Searching....")
    dl_path = f"downloads/{time()}/"
    query_or_search = query if query.startswith("http") else f"ytsearch:{query}"
    if "-m" in message.flags:
        aformat = "mp3"
    else:
        aformat = "opus"
    yt_opts = {
        "logger": FakeLogger(),
        "outtmpl": dl_path + "%(title)s.%(ext)s",
        "format": "bestaudio",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": aformat},
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ],
    }
    ytdl = yt_dlp.YoutubeDL(yt_opts)
    yt_info = await asyncio.to_thread(ytdl.extract_info, query_or_search)
    if not query_or_search.startswith("http"):
        yt_info = yt_info["entries"][0]
    duration = yt_info["duration"]
    artist = yt_info["channel"]
    thumb = await in_memory_dl(yt_info["thumbnail"])
    down_path = glob.glob(dl_path + "*")
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
