import json
from typing import Callable

from pyrogram.errors import MessageNotModified

from app import Config, bot
from app.core import Message


async def init_task():
    chats_id = Config.AUTO_DL_MESSAGE_ID
    blocked_id = Config.BLOCKED_USERS_MESSAGE_ID
    users = Config.USERS_MESSAGE_ID
    disabled = Config.DISABLED_CHATS_MESSAGE_ID

    if chats_id:
        Config.CHATS = json.loads(
            (await bot.get_messages(Config.LOG_CHAT, chats_id)).text
        )
    if blocked_id:
        Config.BLOCKED_USERS = json.loads(
            (await bot.get_messages(Config.LOG_CHAT, blocked_id)).text
        )
    if users:
        Config.USERS = json.loads((await bot.get_messages(Config.LOG_CHAT, users)).text)
    if disabled:
        Config.DISABLED_CHATS = json.loads(
            (await bot.get_messages(Config.LOG_CHAT, disabled)).text
        )


async def add_or_remove(
    mode: str, task: Callable, item: int, config_list: list, message_id: int
) -> None | str:
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


def extract_user(message: Message) -> tuple:
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


def extract_chat(message: Message) -> tuple:
    chat, err = message.input.strip() or message.chat.id, None
    if not Config.AUTO_DL_MESSAGE_ID:
        return chat, "You haven't added `AUTO_DL_MESSAGE_ID` Var, Add it."
    if not chat:
        return chat, "Unable to Extract Chat IDs. Try again."
    try:
        chat = int(chat)
    except ValueError:
        return chat, "Give a Valid chat ID."
    return chat, err


@bot.add_cmd(cmd=["addsudo", "delsudo"])
async def add_or_remove_sudo(bot: bot, message: Message) -> Message | None:
    user, err = extract_user(message)
    if err:
        return await message.reply(err)

    if message.cmd == "addsudo":
        mode: str = "add"
        task: Callable = Config.USERS.append
        action: str = "Added to"
    else:
        mode: str = "remove"
        task: Callable = Config.USERS.remove
        action: str = "Removed from"

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
async def add_or_remove_chat(bot: bot, message: Message) -> Message | None:
    chat, err = extract_chat(message)
    if err:
        return await message.reply(err)

    if message.cmd == "addchat":
        mode: str = "add"
        task: Callable = Config.CHATS.append
        action: str = "Added to"
    else:
        mode: str = "remove"
        task: Callable = Config.CHATS.remove
        action: str = "Removed from"

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
async def block_or_unblock(bot: bot, message: Message) -> Message | None:
    user, err = extract_user(message)
    if err:
        return await message.reply(err)

    if message.cmd == "block":
        mode: str = "add"
        task: Callable = Config.BLOCKED_USERS.append
        action: str = "Added to"
    else:
        mode: str = "remove"
        task: Callable = Config.BLOCKED_USERS.remove
        action: str = "Removed from"

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
async def auto_dl_trigger(bot: bot, message: Message) -> Message | None:
    if not Config.DISABLED_CHATS_MESSAGE_ID:
        return await message.reply("You haven't added `DISABLED_CHATS_ID` Var, Add it.")

    if message.cmd == "disable":
        mode: str = "add"
        task: Callable = Config.DISABLED_CHATS.append
        action: str = "Added to"
    else:
        mode: str = "remove"
        task: Callable = Config.DISABLED_CHATS.remove
        action: str = "Removed from"

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
