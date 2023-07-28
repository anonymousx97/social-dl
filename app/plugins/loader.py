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
    reply = await message.reply("Loading....")
    file_name = message.replied.document.file_name.rstrip(".py")
    reload = sys.modules.pop(f"app.temp.{file_name}", None)
    status = "Reloaded" if reload else "Loaded" 
    plugin = await message.replied.download("app/temp/")
    try:
        importlib.import_module(f"app.temp.{file_name}")
    except BaseException:
        return await reply.edit(str(traceback.format_exc()))
    await reply.edit(f"{status} {file_name}.py.")
