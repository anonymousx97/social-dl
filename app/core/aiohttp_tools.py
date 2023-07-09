import json
import os
from io import BytesIO
from urllib.parse import urlparse

import aiohttp

SESSION = None


async def session_switch():
    if not SESSION:
        globals().update({"SESSION": aiohttp.ClientSession()})
    else:
        await SESSION.close()


async def get_json(url: str, headers: dict = None, params: dict = None, retry: bool = False, json_: bool = False, timeout: int = 10):
    try:
        async with SESSION.get(url=url, headers=headers, params=params, timeout=timeout) as ses:
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
    name = os.path.basename(urlparse(url).path.rstrip("/"))
    if name.endswith(".webp"):
        name = name + ".jpg"
    if name.endswith(".webm"):
        name = name + ".mp4"
    file.name = name
    return file


async def thumb_dl(thumb):
    if not thumb or not thumb.startswith("http"):
        return thumb
    return await in_memory_dl(thumb)
