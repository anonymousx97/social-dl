import os

from pyrogram.enums import ChatType
from pyrogram.errors import BadRequest
from pyrogram.types import Message

from app import bot

# Delete replied and command message


@bot.add_cmd(cmd="del")
async def delete_message(bot, message: Message):
    await message.delete(reply=True)


# Delete Multiple messages from replied to command.
@bot.add_cmd(cmd="purge")
async def purge_(bot, message: Message):
    reply = message.replied
    if not reply:
        return await message.reply("reply to a message")
    start_message = reply.id
    end_message = message.id
    messages = [end_message] + [i for i in range(int(start_message), int(end_message))]
    await bot.delete_messages(chat_id=message.chat.id, message_ids=messages, revoke=True)


@bot.add_cmd(cmd="ids")
async def get_ids(bot, message):
    if reply := message.replied:
        ids = ""
        reply_forward = reply.forward_from_chat
        reply_user = reply.from_user
        ids += f"Chat : `{reply.chat.id}`\n"
        if reply_forward:
            ids += f"Replied {'Channel' if reply_forward.type == ChatType.CHANNEL else 'Chat'} : `{reply_forward.id}`\n"
        if reply_user:
            ids += f"User : {reply.from_user.id}"
    else:
        ids = f"Chat :`{message.chat.id}`"
    await message.reply(ids)


@bot.add_cmd(cmd="join")
async def join_chat(bot, message):
    chat = message.input
    try:
        await bot.join_chat(chat)
    except (KeyError, BadRequest):
        try:
            await bot.join_chat(os.path.basename(chat).strip())
        except Exception as e:
            return await message.reply(str(e))
    await message.reply("Joined")


@bot.add_cmd(cmd="leave")
async def leave_chat(bot, message):
    if message.input:
        chat = message.input
    else:
        chat = message.chat.id
    try:
        await bot.leave_chat(chat)
    except Exception as e:
        await message.reply(str(e))


@bot.add_cmd(cmd="reply")
async def reply(bot, message):
    text = message.input
    await bot.send_message(chat_id=message.chat.id, text=text, reply_to_message_id=message.reply_id, disable_web_page_preview=True)
