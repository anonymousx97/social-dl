import asyncio

from app import bot


@bot.add_cmd(cmd=["cancel", "c"])
async def cancel_task(bot, message):
    task_id = message.reply_id
    if not task_id:
        return await message.reply(
            "Reply To a Command or Bot's Response Message.", del_in=8
        )
    all_tasks = asyncio.all_tasks()
    tasks = [x for x in all_tasks if x.get_name() == f"{message.chat.id}-{task_id}"]
    if not tasks:
        return await message.reply("Task not in Currently Running Tasks.", del_in=8)
    response = ""
    for task in tasks:
        status = task.cancel()
        response += f"Task: __{task.get_name()}__\nCancelled: __{status}__\n"
    await message.reply(response, del_in=5)
