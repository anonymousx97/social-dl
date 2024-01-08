from app import BOT, Config, Message, bot


@bot.add_cmd(cmd="help")
async def cmd_list(bot: BOT, message: Message) -> None:
    """
    CMD: HELP
    INFO: Check info/about available cmds.
    USAGE:
        .help help | .help
    """
    cmd = message.input.strip()
    if not cmd:
        commands: str = "  ".join(
            [
                f"<code>{message.trigger}{cmd}</code>"
                for cmd in sorted(Config.CMD_DICT.keys())
            ]
        )
        await message.reply(
            text=f"<b>Available Commands:</b>\n\n{commands}", del_in=30, block=True
        )
    elif cmd not in Config.CMD_DICT.keys():
        await message.reply(
            f"Invalid <b>{cmd}</b>, check {message.trigger}help", del_in=5
        )
    else:
        await message.reply(
            f"<pre language=js>Doc:{Config.CMD_DICT[cmd].doc}</pre>", del_in=30
        )
