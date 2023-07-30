import asyncio
import traceback

from app import Config, bot
from app.core import filters
from app.core.MediaHandler import ExtractAndSendMedia
from app.core.message import Message

current_tasks = {}


@bot.add_cmd(cmd="dl")
async def dl(bot, message):
    reply = await bot.send_message(
        chat_id=message.chat.id, text="`trying to download...`"
    )
    task = asyncio.Task(ExtractAndSendMedia.process(message))
    current_tasks[reply.id] = task
    media = await task
    if media.exceptions:
        exceptions = "\n".join(media.exceptions)
        await bot.log(
            text=exceptions,
            func="DL",
            chat=message.chat.title or message.chat.first_name,
            name="traceback.txt",
        )
        current_tasks.pop(reply.id)
        return await reply.edit(f"Media Download Failed.")
    if media.media_objects:
        await message.delete()
    await reply.delete()
    current_tasks.pop(reply.id)


@bot.on_message(filters.user_filter)
@bot.on_edited_message(filters.user_filter)
async def cmd_dispatcher(bot, message):
    parsed_message = Message.parse_message(message)
    func = Config.CMD_DICT[parsed_message.cmd]
    try:
        task = asyncio.Task(func(bot, parsed_message))
        current_tasks[message.id] = task
        await task
    except asyncio.exceptions.CancelledError:
        pass
    except BaseException:
        await bot.log(
            text=str(traceback.format_exc()),
            chat=message.chat.title or message.chat.first_name,
            func=func.__name__,
            name="traceback.txt",
        )
    current_tasks.pop(message.id)


@bot.on_message(filters.chat_filter)
async def dl_dispatcher(bot, message):
    parsed_message = Message.parse_message(message)
    try:
        task = asyncio.Task(dl(bot, parsed_message))
        current_tasks[message.id] = task
        await task
    except asyncio.exceptions.CancelledError:
        pass
    except BaseException:
        await bot.log(
            text=str(traceback.format_exc()),
            chat=message.chat.title or message.chat.first_name,
            func=dl.__name__,
            name="traceback.txt",
        )
    current_tasks.pop(message.id)
