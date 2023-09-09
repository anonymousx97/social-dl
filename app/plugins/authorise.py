from pyrogram.errors import MessageNotModified

from app import Config, bot


async def add_or_remove(mode, task, item, config_list, message_id):
    err = None
    if item in config_list and mode == "add":
        return "ID Already in List"
    elif item not in config_list and mode == "remove":
        return "ID Not in List"
    try:
        task(item)
        await bot.edit_message_text(
            chat_id=Config.LOG_CHAT, message_id=message_id, text=str(config_list)
        )
    except MessageNotModified:
        err = "Duplicate Entries, List Not modified."
    except Exception as e:
        err = str(e)
    return err


def extract_user(message):
    user, err = message.input.strip(), None
    if not Config.USERS_MESSAGE_ID:
        return user, "You haven't added `USERS_MESSAGE_ID` Var, Add it."
    if message.replied:
        user = message.replied.from_user.id
    if not user:
        return user, "Unable to Extract User IDs. Try again."
    try:
        user = int(user)
    except ValueError:
        return user, "Give a Valid User ID."
    return user, err


def extract_chat(message):
    chat, err = message.input.strip() or message.chat.id, None
    if not Config.AUTO_DL_MESSAGE_ID:
        return user, "You haven't added `AUTO_DL_MESSAGE_ID` Var, Add it."
    if not chat:
        return user, "Unable to Extract Chat IDs. Try again."
    try:
        chat = int(chat)
    except ValueError:
        return chat, "Give a Valid chat ID."
    return chat, err


@bot.add_cmd(cmd=["addsudo", "delsudo"])
async def add_or_remove_sudo(bot, message):
    user, err = extract_user(message)
    if err:
        return await message.reply(err)

    if message.cmd == "addsudo":
        mode = "add"
        task = Config.USERS.append
        action = "Added to"
    else:
        mode = "remove"
        task = Config.USERS.remove
        action = "Removed from"

    if err := await add_or_remove(
        mode=mode,
        task=task,
        item=user,
        config_list=Config.USERS,
        message_id=Config.USERS_MESSAGE_ID,
    ):
        return await message.reply(err, del_in=5)
    await message.reply(f"User {action} Authorised List.", del_in=5)


@bot.add_cmd(cmd=["addchat", "delchat"])
async def add_or_remove_chat(bot, message):
    chat, err = extract_chat(message)
    if err:
        return await message.reply(err)

    if message.cmd == "addchat":
        mode = "add"
        task = Config.CHATS.append
        action = "Added to"
    else:
        mode = "remove"
        task = Config.CHATS.remove
        action = "Removed from"

    if err := await add_or_remove(
        mode=mode,
        task=task,
        item=chat,
        config_list=Config.CHATS,
        message_id=Config.AUTO_DL_MESSAGE_ID,
    ):
        return await message.reply(err, del_in=5)
    await message.reply(
        f"<b>{message.chat.title or message.chat.first_name}</b> {action} Authorised List.",
        del_in=5,
    )


@bot.add_cmd(cmd=["block", "unblock"])
async def block_or_unblock(bot, message):
    user, err = extract_user(message)
    if err:
        return await message.reply(err)

    if message.cmd == "block":
        mode = "add"
        task = Config.BLOCKED_USERS.append
        action = "Added to"
    else:
        mode = "remove"
        task = Config.BLOCKED_USERS.remove
        action = "Removed from"

    if err := await add_or_remove(
        mode=mode,
        task=task,
        item=user,
        config_list=Config.BLOCKED_USERS,
        message_id=Config.BLOCKED_USERS_MESSAGE_ID,
    ):
        return await message.reply(err, del_in=5)
    await message.reply(f"User {action} Ban List.", del_in=5)


@bot.add_cmd(cmd=["enable", "disable"])
async def auto_dl_trigger(bot, message):
    if not Config.DISABLED_CHATS_MESSAGE_ID:
        return await message.reply("You haven't added `DISABLED_CHATS_ID` Var, Add it.")

    if message.cmd == "disable":
        mode = "add"
        task = Config.DISABLED_CHATS.append
        action = "Added to"
    else:
        mode = "remove"
        task = Config.DISABLED_CHATS.remove
        action = "Removed from"

    if err := await add_or_remove(
        mode=mode,
        task=task,
        item=message.chat.id,
        config_list=Config.DISABLED_CHATS,
        message_id=Config.DISABLED_CHATS_MESSAGE_ID,
    ):
        return await message.reply(err, del_in=5)
    await message.reply(
        f"<b>{message.chat.title or message.chat.first_name}</b> {action} Disabled List.",
        del_in=5,
    )
