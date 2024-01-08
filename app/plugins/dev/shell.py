import asyncio
import inspect

from pyrogram.enums import ParseMode

from app import BOT, Config, Message
from app.utils import shell


async def run_cmd(bot: BOT, message: Message) -> Message | None:
    cmd: str = message.input.strip()
    reply: Message = await message.reply("executing...")
    try:
        proc_stdout: str = await asyncio.Task(
            shell.run_shell_cmd(cmd), name=reply.task_id
        )
    except asyncio.exceptions.CancelledError:
        return await reply.edit("`Cancelled...`")
    output: str = f"<pre language=shell>~${cmd}\n\n{proc_stdout}</pre>"
    return await reply.edit(output, name="sh.txt", disable_web_page_preview=True)


# Shell with Live Output
async def live_shell(bot: BOT, message: Message) -> Message | None:
    cmd: str = message.input.strip()
    reply: Message = await message.reply("`getting live output....`")
    sub_process: shell.AsyncShell = await shell.AsyncShell.run_cmd(cmd)
    sleep_for: int = 1
    output: str = ""
    try:
        async for stdout in sub_process.get_output():
            if output != stdout:
                if len(stdout) <= 4096:
                    await reply.edit(
                        f"```shell\n{stdout}```",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                output = stdout
            if sleep_for >= 6:
                sleep_for = 1
            await asyncio.Task(asyncio.sleep(sleep_for), name=reply.task_id)
            sleep_for += 1
        return await reply.edit(
            f"<pre language=shell>~${cmd}\n\n{sub_process.full_std}</pre>",
            name="shell.txt",
            disable_web_page_preview=True,
        )
    except asyncio.exceptions.CancelledError:
        sub_process.cancel()
        return await reply.edit(f"`Cancelled....`")


if Config.DEV_MODE:
    Config.CMD_DICT["shell"] = Config.CMD(
        func=live_shell, path=inspect.stack()[0][1], doc=live_shell.__doc__
    )
    Config.CMD_DICT["sh"] = Config.CMD(
        func=run_cmd, path=inspect.stack()[0][1], doc=run_cmd.__doc__
    )
