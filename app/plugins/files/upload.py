import asyncio
import os
import time

from app import BOT, Config, bot
from app.core import Message
from app.utils.downloader import Download, DownloadedFile
from app.utils.helpers import progress
from app.utils.media_helper import MediaType, bytes_to_mb
from app.utils.shell import check_audio, get_duration, take_ss


async def video_upload(
    file: DownloadedFile, has_spoiler: bool
) -> dict[str, bot.send_video, bot.send_animation, dict]:
    thumb = await take_ss(file.full_path, path=file.path)
    if not (await check_audio(file.full_path)):  # fmt:skip
        return dict(
            method=bot.send_animation,
            kwargs=dict(
                thumb=thumb,
                unsave=True,
                animation=file.full_path,
                duration=await get_duration(file.full_path),
                has_spoiler=has_spoiler,
            ),
        )
    return dict(
        method=bot.send_video,
        kwargs=dict(
            thumb=thumb,
            video=file.full_path,
            duration=await get_duration(file.full_path),
            has_spoiler=has_spoiler,
        ),
    )


async def photo_upload(
    file: DownloadedFile, has_spoiler: bool
) -> dict[str, bot.send_photo, dict]:
    return dict(
        method=bot.send_photo,
        kwargs=dict(photo=file.full_path, has_spoiler=has_spoiler),
    )


async def audio_upload(
    file: DownloadedFile, has_spoiler: bool
) -> dict[str, bot.send_audio, dict]:
    return dict(
        method=bot.send_audio,
        kwargs=dict(
            audio=file.full_path, duration=await get_duration(file=file.full_path)
        ),
    )


async def doc_upload(
    file: DownloadedFile, has_spoiler: bool
) -> dict[str, bot.send_document, dict]:
    return dict(
        method=bot.send_document,
        kwargs=dict(document=file.full_path, force_document=True),
    )


FILE_TYPE_MAP = {
    MediaType.PHOTO: photo_upload,
    MediaType.DOCUMENT: doc_upload,
    MediaType.GIF: video_upload,
    MediaType.AUDIO: audio_upload,
    MediaType.VIDEO: video_upload,
}


def file_check(file: str):
    return os.path.isfile(file)


@bot.add_cmd(cmd="upload")
async def upload(bot: BOT, message: Message):
    """
    CMD: UPLOAD
    INFO: Upload Media/Local Files/Plugins to TG.
    FLAGS:
        -d: to upload as doc.
        -s: spoiler.
    USAGE:
        .upload [-d] URL | Path to File | CMD
    """
    input = message.flt_input
    if not input:
        await message.reply("give a file url | path to upload.")
        return
    response = await message.reply("checking input...")
    if input in Config.CMD_DICT.keys():
        await message.reply_document(document=Config.CMD_DICT[input].path)
        await response.delete()
        return
    elif input.startswith("http") and not file_check(input):
        dl_obj: Download = await Download.setup(
            url=input,
            path=os.path.join("downloads", str(time.time())),
            message_to_edit=response,
        )
        if not bot.me.is_premium and dl_obj.size > 1999:
            await response.edit(
                "<b>Aborted</b>, File size exceeds 2gb limit for non premium users!!!"
            )
            return
        try:
            file: DownloadedFile = await dl_obj.download()
        except asyncio.exceptions.CancelledError:
            await response.edit("Cancelled...")
            return
        except TimeoutError:
            await response.edit("Download Timeout...")
            return
    elif file_check(input):
        file = DownloadedFile(
            name=input,
            path=os.path.dirname(input),
            full_path=input,
            size=bytes_to_mb(os.path.getsize(input)),
        )
    else:
        await response.edit("invalid `cmd` | `url` | `file path`!!!")
        return
    await response.edit("uploading....")
    progress_args = (response, "Uploading...", file.name, file.full_path)
    if "-d" in message.flags:
        media: dict = dict(
            method=bot.send_document,
            kwargs=dict(document=file.full_path, force_document=True),
        )
    else:
        media: dict = await FILE_TYPE_MAP[file.type](
            file, has_spoiler="-s" in message.flags
        )
    try:
        await media["method"](
            chat_id=message.chat.id,
            reply_to_message_id=message.reply_id,
            progress=progress,
            progress_args=progress_args,
            **media["kwargs"]
        )
        await response.delete()
    except asyncio.exceptions.CancelledError:
        await response.edit("Cancelled....")
