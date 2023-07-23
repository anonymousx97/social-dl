import os

from pyrogram.enums import ChatType

from app import Config, bot


@bot.add_cmd(cmd="bot")
async def info(bot, message):
    head = "<b><a href=https://t.me/Social_DL>Social-DL</a> is running.</b>"
    chat_count = f"\n<b>Auto-Dl enabled in: <code>{len(Config.CHATS)}</code> chats</b>\n"
    supported_sites, photo = await bot.get_messages("Social_DL", [2, 3])
    await photo.copy(message.chat.id, caption="\n".join([head, chat_count, supported_sites.text.html]))

@bot.add_cmd(cmd="help")
async def help(bot, message):
    commands = "\n".join([ f"<code>{Config.TRIGGER}{i}</code>" for i in Config.CMD_DICT.keys()])
    await message.reply(f"<b>Available Commands:</b>\n\n{commands}")

@bot.add_cmd(cmd="restart")
async def restart(bot, message):
    reply = await message.reply("restarting....")
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        os.environ["RESTART_MSG"] = str(reply.id)
        os.environ["RESTART_CHAT"] = str(reply.chat.id)
    await bot.restart()


@bot.add_cmd(cmd="update")
async def chat_update(bot, message):
    await bot.set_filter_list()
    await message.reply("Filters Refreshed")