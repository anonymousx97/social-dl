import asyncio
import os

from async_lru import alru_cache
from git import Repo
from pyrogram.enums import ChatType

from app import Config, Message, bot


@alru_cache()
async def get_banner() -> Message:
    return await bot.get_messages("Social_DL", [2, 3])


@bot.add_cmd(cmd="bot")
async def info(bot, message):
    head = "<b><a href=https://t.me/Social_DL>Social-DL</a> is running.</b>"
    chat_count = (
        f"\n<b>Auto-Dl enabled in: <code>{len(Config.CHATS)}</code> chats</b>\n"
    )
    supported_sites, photo = await get_banner()
    await photo.copy(
        message.chat.id,
        caption="\n".join([head, chat_count, supported_sites.text.html]),
    )


@bot.add_cmd(cmd="help")
async def cmd_list(bot: bot, message: Message) -> None:
    commands: str = "\n".join(
        [f"<code>{Config.TRIGGER}{i}</code>" for i in Config.CMD_DICT.keys()]
    )
    await message.reply(f"<b>Available Commands:</b>\n\n{commands}", del_in=30)


@bot.add_cmd(cmd="restart")
async def restart(bot: bot, message: Message, u_resp: Message | None = None) -> None:
    reply: Message = u_resp or await message.reply("restarting....")
    if reply.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        os.environ["RESTART_MSG"] = str(reply.id)
        os.environ["RESTART_CHAT"] = str(reply.chat.id)
    await bot.restart(hard="-h" in message.flags)


@bot.add_cmd(cmd="refresh")
async def chat_update(bot: bot, message: Message) -> None:
    await bot.set_filter_list()
    await message.reply("Filters Refreshed", del_in=8)


@bot.add_cmd(cmd="repo")
async def sauce(bot: bot, message: Message) -> None:
    await bot.send_message(
        chat_id=message.chat.id,
        text="<a href='https://github.com/anonymousx97/social-dl'>Social-DL</a>",
        reply_to_message_id=message.reply_id or message.id,
        disable_web_page_preview=True,
    )


@bot.add_cmd(cmd="update")
async def updater(bot: bot, message: Message) -> None | Message:
    reply: Message = await message.reply("Checking for Updates....")
    repo: Repo = Repo()
    repo.git.fetch()
    commits: str = ""
    limit: int = 0
    for commit in repo.iter_commits("HEAD..origin/main"):
        commits += f"""
<b>#{commit.count()}</b> <a href='{Config.UPSTREAM_REPO}/commit/{commit}'>{commit.summary}</a> By <i>{commit.author}</i>
"""
        limit += 1
        if limit > 50:
            break
    if not commits:
        return await reply.edit(text="Already Up To Date.", del_in=5)
    if "-pull" not in message.flags:
        return await reply.edit(
            text=f"<b>Update Available:</b>\n\n{commits}", disable_web_page_preview=True
        )
    repo.git.reset("--hard")
    repo.git.pull(Config.UPSTREAM_REPO, "--rebase=true")
    await asyncio.gather(
        bot.log(text=f"#Updater\nPulled:\n\n{commits}", disable_web_page_preview=True),
        reply.edit("<b>Update Found</b>\n<i>Pulling....</i>"),
    )
    await restart(bot, message, reply)
