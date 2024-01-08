from app import BOT, Message, bot


@bot.add_cmd(cmd="click")
async def click(bot: BOT, message: Message):
    if not message.input or not message.replied:
        await message.reply(
            "reply to a message containing a button and give a button to click"
        )
        return
    try:
        await message.replied.click(message.input.strip())
    except Exception as e:
        await message.reply(str(e), del_in=5)
