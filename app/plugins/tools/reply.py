from app import BOT, Message, bot
from app.plugins.tools.get_message import parse_link


@bot.add_cmd(cmd="reply")
async def reply(bot: BOT, message: Message) -> None:
    """
    CMD: REPLY
    INFO: Reply to a Message.
    FLAGS: -r to reply remotely using message link.
    USAGE:
        .reply HI | .reply -r t.me/... HI
    """
    if "-r" in message.flags:
        input: list[str] = message.flt_input.split(" ", maxsplit=1)
        if len(input) < 2:
            await message.reply("The '-r' flag requires a message link and text.")
            return
        message_link, text = input
        chat_id, reply_to_message_id = parse_link(message_link.strip())
    else:
        text: str = message.input
        chat_id = message.chat.id
        reply_to_message_id = message.reply_id
    if not text:
        return
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_to_message_id=reply_to_message_id,
        disable_web_page_preview=True,
    )
