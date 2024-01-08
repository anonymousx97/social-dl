import asyncio
from typing import Awaitable

from pyrogram.types import User

from app import BOT, Message, bot


@bot.add_cmd(cmd=["ban", "unban"])
async def ban_or_unban(bot: BOT, message: Message) -> None:
    user, reason = await message.extract_user_n_reason()
    if not isinstance(user, User):
        await message.reply(user, del_in=10)
        return
    if message.cmd == "ban":
        action: Awaitable = bot.ban_chat_member(
            chat_id=message.chat.id, user_id=user.id
        )
    else:
        action: Awaitable = bot.unban_chat_member(
            chat_id=message.chat.id, user_id=user.id
        )
    try:
        await action
        await message.reply(
            text=f"{message.cmd.capitalize()}ned: {user.mention}\nReason: {reason}."
        )
    except Exception as e:
        await message.reply(text=e, del_in=10)


@bot.add_cmd(cmd="kick")
async def kick_user(bot: BOT, message: Message):
    user, reason = await message.extract_user_n_reason()
    if not isinstance(user, User):
        await message.reply(user, del_in=10)
        return
    try:
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=user.id)
        await asyncio.sleep(1)
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=user.id)
        await message.reply(
            text=f"{message.cmd.capitalize()}ed: {user.mention}\nReason: {reason}."
        )
    except Exception as e:
        await message.reply(text=e, del_in=10)
