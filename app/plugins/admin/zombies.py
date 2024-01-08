import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait

from app import BOT, Message, bot


@bot.add_cmd(cmd="zombies")
async def clean_zombies(bot: BOT, message: Message):
    me = await bot.get_chat_member(message.chat.id, bot.me.id)
    if me.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
        await message.reply("Cannot clean zombies without being admin.")
        return
    zombies = 0
    admin_zombies = 0
    response = await message.reply("Cleaning Zombies....\nthis may take a while")
    async for member in bot.get_chat_members(message.chat.id):
        try:
            if member.user.is_deleted:
                if member.status in {
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                }:
                    admin_zombies += 1
                    continue
                zombies += 1
                await bot.ban_chat_member(
                    chat_id=message.chat.id, user_id=member.user.id
                )
                await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.value + 3)
    resp_str = f"Cleaned <b>{zombies}</b> zombies."
    if admin_zombies:
        resp_str += f"\n<b>{admin_zombies}</b> Admin Zombie(s) not Removed."
    await response.edit(resp_str)
