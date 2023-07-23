import importlib
import sys
import traceback

from app import bot

@bot.add_cmd(cmd="load")
async def loader(bot, message):
    if (
        not message.replied
        or not message.replied.document
        or not message.replied.document.file_name.endswith(".py")
    ):
        return await message.reply("reply to a plugin.")
    file_name = message.replied.document.file_name.rstrip(".py")
    sys.modules.pop(f"app.temp.{file_name}", None)
    plugin = await message.replied.download("app/temp/")
    try:
        importlib.import_module(f"app.temp.{file_name}")
    except BaseException:
        return await message.reply(str(traceback.format_exc()))
    await message.reply(f"Loaded {file_name}.py.")
