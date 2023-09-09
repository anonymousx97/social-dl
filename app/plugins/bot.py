import asyncio
import os

from git import Repo
from pyrogram.enums import ChatType

from app import Config, bot


@bot.add_cmd(cmd="bot")
async def info(bot, message):
    head = "<b><a href=https://t.me/Social_DL>Social-DL</a> is running.</b>"
    chat_count = (
        f"\n<b>Auto-Dl enabled in: <code>{len(Config.CHATS)}</code> chats</b>\n"
    )
    supported_sites, photo = await bot.get_messages("Social_DL", [2, 3])
    await photo.copy(
        message.chat.id,
        caption="\n".join([head, chat_count, supported_sites.text.html]),
    )


@bot.add_cmd(cmd="help")
async def help(bot, message):
    commands = "\n".join(
        [f"<code>{Config.TRIGGER}{i}</code>" for i in Config.CMD_DICT.keys()]
    )
    await message.reply(f"<b>Available Commands:</b>\n\n{commands}", del_in=30)


@bot.add_cmd(cmd="restart")
async def restart(bot, message, u_resp=None):
    reply = u_resp or await message.reply("restarting....")
    if reply.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        os.environ["RESTART_MSG"] = str(reply.id)
        os.environ["RESTART_CHAT"] = str(reply.chat.id)
    await bot.restart()


@bot.add_cmd(cmd="refresh")
async def chat_update(bot, message):
    await bot.set_filter_list()
    await message.reply("Filters Refreshed", del_in=8)


@bot.add_cmd(cmd="repo")
async def sauce(bot, message):
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"<a href='{Config.UPSTREAM_REPO}'>Social-DL</a>",
        reply_to_message_id=message.reply_id or message.id,
        disable_web_page_preview=True,
    )


@bot.add_cmd(cmd="update")
async def updater(bot, message):
    reply = await message.reply("Checking for Updates....")
    repo = Repo()
    repo.git.fetch()
    commits = ""
    limit = 0
    for commit in repo.iter_commits("HEAD..origin/main"):
        commits += f"<b>#{commit.count()}</b> <a href='{Config.UPSTREAM_REPO}/commit/{commit}'>{commit.summary}</a> By <i>{commit.author}</i>\n\n"
        limit += 1
        if limit > 50:
            break
    if not commits:
        return await reply.edit("Already Up To Date.", del_in=5)
    if "-pull" not in message.flags:
        return await reply.edit(f"<b>Update Available:</b>\n\n{commits}")
    repo.git.reset("--hard")
    repo.git.pull(Config.UPSTREAM_REPO, "--rebase=true")
    await asyncio.gather(
        bot.log(text=f"#Updater\nPulled:\n\n{commits}"),
        reply.edit("<b>Update Found</b>\n<i>Pulling....</i>"),
    )
    await restart(bot, message, reply)
