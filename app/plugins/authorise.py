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


@bot.add_cmd(cmd="addsudo")
async def add_sudo(bot, message):
    user, err = extract_user(message)
    if err:
        return await message.reply(err)
    if err := await add_or_remove(
        mode="add",
        task=Config.USERS.append,
        item=user,
        config_list=Config.USERS,
        message_id=Config.USERS_MESSAGE_ID,
    ):
        return await message.reply(err)
    await message.reply("User Added to Authorised List.")


@bot.add_cmd(cmd="delsudo")
async def add_sudo(bot, message):
    user, err = extract_user(message)
    if err:
        return await message.reply(err)
    if err := await add_or_remove(
        mode="remove",
        task=Config.USERS.remove,
        item=user,
        config_list=Config.USERS,
        message_id=Config.USERS_MESSAGE_ID,
    ):
        return await message.reply(err)
    await message.reply("User Removed from Authorised List.")


@bot.add_cmd(cmd="addchat")
async def add_chat(bot, message):
    chat, err = extract_chat(message)
    if err:
        return await message.reply(err)
    if err := await add_or_remove(
        mode="add",
        task=Config.CHATS.append,
        item=chat,
        config_list=Config.CHATS,
        message_id=Config.AUTO_DL_MESSAGE_ID,
    ):
        return await message.reply(err)
    await message.reply(f"<b>{message.chat.title}</b> Added to Authorised List.")


@bot.add_cmd(cmd="delchat")
async def add_chat(bot, message):
    chat, err = extract_chat(message)
    if err:
        return await message.reply(err)
    if err := await add_or_remove(
        mode="remove",
        task=Config.CHATS.remove,
        item=chat,
        config_list=Config.CHATS,
        message_id=Config.AUTO_DL_MESSAGE_ID,
    ):
        return await message.reply(err)
    await message.reply(f"<b>{message.chat.title}</b> Added Removed from Authorised List.")



@bot.add_cmd(cmd="block")
async def add_sudo(bot, message):
    user, err = extract_user(message)
    if err:
        return await message.reply(err)
    if err := await add_or_remove(
        mode="add",
        task=Config.BLOCKED_USERS.append,
        item=user,
        config_list=Config.BLOCKED_USERS,
        message_id=Config.BLOCKED_USERS_MESSAGE_ID,
    ):
        return await message.reply(err)
    await message.reply("User Added to Ban List.")


@bot.add_cmd(cmd="unblock")
async def add_sudo(bot, message):
    user, err = extract_user(message)
    if err:
        return await message.reply(err)
    if err := await add_or_remove(
        mode="remove",
        task=Config.BLOCKED_USERS.remove,
        item=user,
        config_list=Config.BLOCKED_USERS,
        message_id=Config.BLOCKED_USERS_MESSAGE_ID,
    ):
        return await message.reply(err)
    await message.reply("User Removed from Ban List.")



