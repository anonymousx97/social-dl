import json
from io import BytesIO

import aiohttp

from app.utils.media_helper import get_filename

SESSION: aiohttp.ClientSession | None = None


async def init_task() -> None:
    if not SESSION:
        globals().update({"SESSION": aiohttp.ClientSession()})
    else:
        await SESSION.close()


async def get_json(
    url: str,
    headers: dict = None,
    params: dict | str = None,
    json_: bool = False,
    timeout: int = 10,
) -> dict | None:
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


async def in_memory_dl(url: str) -> BytesIO:
    async with SESSION.get(url) as remote_file:
        bytes_data = await remote_file.read()
    file = BytesIO(bytes_data)
    file.name = get_filename(url)
    return file


async def thumb_dl(thumb) -> BytesIO | str | None:
    if not thumb or not thumb.startswith("http"):
        return thumb
    return await in_memory_dl(thumb)  # NOQA
