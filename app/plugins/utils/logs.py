import aiofiles

from app import BOT, bot
from app.core import Message


@bot.add_cmd(cmd="logs")
async def read_logs(bot: BOT, message: Message):
    async with aiofiles.open("logs/app_logs.txt", "r") as aio_file:
        text = await aio_file.read()
    if len(text) < 4050:
        await message.reply(f"<pre language=bash>{text}</pre>")
    else:
        await message.reply_document(document="logs/app_logs.txt")
