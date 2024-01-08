import os

from pyrogram.enums import ChatType
from pyrogram.errors import BadRequest

from app import BOT, Message, bot


@bot.add_cmd(cmd="ids")
async def get_ids(bot: BOT, message: Message) -> None:
    reply: Message = message.replied
    if reply:
        ids: str = ""
        reply_forward = reply.forward_from_chat
        reply_user = reply.from_user
        ids += f"<b>Chat</b> : `{reply.chat.id}`\n"
        if reply_forward:
            ids += f"<b>Replied {'Channel' if reply_forward.type == ChatType.CHANNEL else 'Chat'}</b> : `{reply_forward.id}`\n"
        if reply_user:
            ids += f"<b>User</b> : {reply.from_user.id}"
    elif message.input:
        ids: int = (await bot.get_chat(message.input[1:])).id
    else:
        ids: str = f"<b>Chat</b> :`{message.chat.id}`"
    await message.reply(ids)


@bot.add_cmd(cmd="join")
async def join_chat(bot: BOT, message: Message) -> None:
    chat: str = message.input
    try:
        await bot.join_chat(chat)
    except (KeyError, BadRequest):
        try:
            await bot.join_chat(os.path.basename(chat).strip())
        except Exception as e:
            await message.reply(str(e))
            return
    await message.reply("Joined")


@bot.add_cmd(cmd="leave")
async def leave_chat(bot: BOT, message: Message) -> None:
    if message.input:
        chat = message.input
    else:
        chat = message.chat.id
        await message.reply(
            text=f"Leaving current chat in 5\nReply with `{message.trigger}c` to cancel",
            del_in=5,
            block=True,
        )
    try:
        await bot.leave_chat(chat)
    except Exception as e:
        await message.reply(str(e))
