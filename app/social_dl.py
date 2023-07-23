import traceback
from app import Config, bot
from app.core import filters
from app.core.MediaHandler import ExtractAndSendMedia
from app.core.message import Message


@bot.add_cmd(cmd="dl")
async def dl(bot, message):
    reply = await bot.send_message(chat_id=message.chat.id, text="`trying to download...`")
    media = await ExtractAndSendMedia.process(message)
    if media.exceptions:
        exceptions = "\n".join(media.exceptions)
        await bot.log(text=exceptions, func="DL", chat=message.chat.title or message.chat.first_name, name="traceback.txt")
        return await reply.edit(f"Media Download Failed.")
    if media.media_objects:
        await message.delete()
    await reply.delete()


@bot.on_message(filters.user_filter)
@bot.on_edited_message(filters.user_filter)
async def cmd_dispatcher(bot, message):
    func = Config.CMD_DICT[message.text.split(maxsplit=1)[0].lstrip(Config.TRIGGER)]
    parsed_message = Message.parse_message(message)
    try:
        await func(bot, parsed_message)
    except BaseException:
        await bot.log(text=str(traceback.format_exc()), chat=message.chat.title or message.chat.first_name, func=func.__name__, name="traceback.txt")


@bot.on_message(filters.chat_filter)
async def dl_dispatcher(bot, message):
    func = Config.CMD_DICT["dl"]
    parsed_message = Message.parse_message(message)
    try:
        await func(bot, parsed_message)
    except BaseException:
        await bot.log(text=str(traceback.format_exc()), chat=message.chat.title or message.chat.first_name, func=func.__name__, name="traceback.txt")
