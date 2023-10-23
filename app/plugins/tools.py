import asyncio

from app import Message, bot


@bot.add_cmd(cmd="c")
async def cancel_task(bot: bot, message: Message) -> Message | None:
    task_id: str | None = message.replied_task_id
    if not task_id:
        return await message.reply(
            text="Reply To a Command or Bot's Response Message.", del_in=8
        )
    all_tasks: set[asyncio.all_tasks] = asyncio.all_tasks()
    tasks: list[asyncio.Task] | None = [x for x in all_tasks if x.get_name() == task_id]
    if not tasks:
        return await message.reply(
            text="Task not in Currently Running Tasks.", del_in=8
        )
    response: str = ""
    for task in tasks:
        status: bool = task.cancel()
        response += f"Task: __{task.get_name()}__\nCancelled: __{status}__\n"
    await message.reply(response, del_in=5)
