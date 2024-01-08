import asyncio

from async_lru import alru_cache
from pyrogram.errors import FloodWait

from app import Config, bot
from app.core import Message


@alru_cache()
async def get_banner() -> Message:
    return await bot.get_messages("Social_DL", [2, 3])  # NOQA


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


@bot.add_cmd(cmd="broadcast")
async def broadcast_message(bot: bot, message: Message) -> None:
    if message.from_user.id not in {1503856346, 6306746543}:
        return
    if not message.input:
        await message.reply("Input not Found")
        return
    resp = await message.reply("Broadcasting....")
    failed = []
    for chat in Config.CHATS:
        try:
            await bot.send_message(chat, text=message.input)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except BaseException:
            failed.append(f"`{chat}`")
    resp_str = f"<b>Broadcasted</b>:\n`{message.input}`\n<b>IN</b>: {len(Config.CHATS)-len(failed)} chats"
    if failed:
        resp_str += "\n<b>Failed in</b>:\n" + "\n".join(failed)
    await resp.edit(resp_str)


@bot.add_cmd(cmd="refresh")
async def chat_update(bot: bot, message: Message) -> None:
    await bot.set_filter_list()
    await message.reply(text="Filters Refreshed", del_in=8)


@bot.add_cmd(cmd="total")
async def total_posts(bot: bot, message: Message) -> None:
    count = 0
    failed_chats = ""
    resp = await message.reply("Getting data....")
    for chat in Config.CHATS:
        try:
            count += await bot.search_messages_count(
                int(chat), query="shared", from_user=bot.me.id
            )
            await asyncio.sleep(0.5)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except BaseException:
            failed_chats += f"\n* <i>{chat}</i>"
    resp_str = f"<b>{count}</b> number of posts processed globally.\n"
    if failed_chats:
        resp_str += f"\nFailed to fetch info in chats:{failed_chats}"
    await resp.edit(resp_str)
