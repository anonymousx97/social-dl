from app import bot
from app.social_dl import current_tasks


@bot.add_cmd(cmd="cancel")
async def cancel_task(bot, message):
    task_id = message.reply_id
    if not task_id:
        return await message.reply("Reply To a Command or Bot's Response Message.")
    task = current_tasks.get(task_id)
    if not task:
        return await message.reply("Task not in Currently Running Tasks.")
    reply = await message.reply("Cancelling....")
    cancelled = task.cancel()
    if cancelled:
        response = "Task Cancelled Successfully."
    else:
        response = "Task not Running.\nIt either is Finished or has Errored."
    await reply.edit(response)
