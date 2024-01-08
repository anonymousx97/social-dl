from urllib.parse import urlparse

from app import BOT, Message, bot


def parse_link(link: str) -> tuple[int | str, int]:
    parsed_url: str = urlparse(link).path.strip("/")
    chat, id = parsed_url.lstrip("c/").split("/")
    if chat.isdigit():
        chat = int(f"-100{chat}")
    return chat, int(id)


@bot.add_cmd(cmd="gm")
async def get_message(bot: BOT, message: Message):
    """
    CMD: Get Message
    INFO: Get a Message Json/Attr by providing link.
    USAGE:
        .gm t.me/.... | .gm t.me/... text [Returns message text]
    """
    if not message.input:
        await message.reply("Give a Message link.")
    attr = None
    if len(message.text_list) == 3:
        link, attr = message.text_list[1:]
    else:
        link = message.input.strip()
    remote_message = await bot.get_messages(*parse_link(link))
    if not attr:
        await message.reply(str(remote_message))
        return
    if hasattr(remote_message, attr):
        await message.reply(str(getattr(remote_message, attr)))
        return
    await message.reply(f"Message object has no attribute '{attr}'")
