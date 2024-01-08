import asyncio

from pyrogram.types import ChatPrivileges, User

from app import BOT, Message, bot


def get_privileges(
    anon: bool = False, full: bool = False, without_rights: bool = False
) -> ChatPrivileges:
    if without_rights:
        return ChatPrivileges(
            can_manage_chat=True,
            can_manage_video_chats=False,
            can_pin_messages=False,
            can_delete_messages=False,
            can_change_info=False,
            can_restrict_members=False,
            can_invite_users=False,
            can_promote_members=False,
            is_anonymous=False,
        )
    return ChatPrivileges(
        can_manage_chat=True,
        can_manage_video_chats=True,
        can_pin_messages=True,
        can_delete_messages=True,
        can_change_info=True,
        can_restrict_members=True,
        can_invite_users=True,
        can_promote_members=full,
        is_anonymous=anon,
    )


@bot.add_cmd(cmd=["promote", "demote"])
async def promote_or_demote(bot: BOT, message: Message) -> None:
    """
    CMD: PROMOTE | DEMOTE
    INFO: Add/Remove an Admin.
    FLAGS:
        PROMOTE: -full for full rights, -anon for anon admin
    USAGE:
        PROMOTE: .promote [ -anon | -full ] [ UID | REPLY | @ ] Title[Optional]
        DEMOTE: .demote [ UID | REPLY | @ ]
    """
    response: Message = await message.reply(
        f"Trying to {message.cmd.capitalize()}....."
    )
    user, title = await message.extract_user_n_reason()
    if not isinstance(user, User):
        await response.edit(user, del_in=10)
        return
    full: bool = "-full" in message.flags
    anon: bool = "-anon" in message.flags
    without_rights = "-wr" in message.flags
    promote = message.cmd == "promote"
    if promote:
        privileges: ChatPrivileges = get_privileges(
            full=full, anon=anon, without_rights=without_rights
        )
    else:
        privileges = ChatPrivileges(can_manage_chat=False)
    response_text = f"{message.cmd.capitalize()}d: {user.mention}"
    try:
        await bot.promote_chat_member(
            chat_id=message.chat.id, user_id=user.id, privileges=privileges
        )
        if promote:
            # Let server promote admin before setting title
            # Bot is too fast moment 😂😂😂
            await asyncio.sleep(1)
            await bot.set_administrator_title(
                chat_id=message.chat.id, user_id=user.id, title=title or "Admin"
            )
            if title:
                response_text += f"\nTitle: {title}"
            if without_rights:
                response_text += "\nWithout Rights: True"
        await response.edit(text=response_text)
    except Exception as e:
        await response.edit(text=e, del_in=10, block=True)
