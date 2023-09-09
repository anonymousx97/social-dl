import json
from io import BytesIO
from os.path import basename, splitext
from urllib.parse import urlparse

import aiohttp

from app.core.scraper_config import MediaType

SESSION = None


async def session_switch():
    if not SESSION:
        globals().update({"SESSION": aiohttp.ClientSession()})
    else:
        await SESSION.close()


async def get_json(
    url: str,
    headers: dict = None,
    params: dict = None,
    json_: bool = False,
    timeout: int = 10,
):
    try:
        async with SESSION.get(
            url=url, headers=headers, params=params, timeout=timeout
        ) as ses:
            if json_:
                ret_json = await ses.json()
            else:
                ret_json = json.loads(await ses.text())
            return ret_json
    except BaseException:
        return


async def in_memory_dl(url: str):
    async with SESSION.get(url) as remote_file:
        bytes_data = await remote_file.read()
    file = BytesIO(bytes_data)
    file.name = get_filename(url)
    return file


def get_filename(url):
    name = basename(urlparse(url).path.rstrip("/")).lower()
    if name.endswith((".webp", ".heic")):
        name = name + ".jpg"
    if name.endswith(".webm"):
        name = name + ".mp4"
    return name


def get_type(url):
    name, ext = splitext(get_filename(url))
    if ext in {".png", ".jpg", ".jpeg"}:
        return MediaType.PHOTO
    if ext in {".mp4", ".mkv", ".webm"}:
        return MediaType.VIDEO
    if ext in {".gif"}:
        return MediaType.GIF


async def thumb_dl(thumb):
    if not thumb or not thumb.startswith("http"):
        return thumb
    return await in_memory_dl(thumb)
