import asyncio
import inspect
import sys
import traceback
from io import StringIO

from pyrogram.enums import ParseMode

from app import Config, bot, BOT, Message  # isort:skip
from app.utils import shell, aiohttp_tools as aio  # isort:skip


async def executor(bot: BOT, message: Message) -> Message | None:
    """
    CMD: EXEC
    INFO: Run Python Code.
    FLAGS: -s to only show output.
    USAGE:
        .exec [-s] return 1
    """
    code: str = message.flt_input.strip()
    if not code:
        return await message.reply("exec Jo mama?")
    reply: Message = await message.reply("executing")
    sys.stdout = codeOut = StringIO()
    sys.stderr = codeErr = StringIO()
    # Indent code as per proper python syntax
    formatted_code = "\n    ".join(code.splitlines())
    try:
        # Create and initialise the function
        exec(f"async def _exec(bot, message):\n    {formatted_code}")
        task = asyncio.Task(locals()["_exec"](bot, message), name=reply.task_id)
        func_out = await task
    except asyncio.exceptions.CancelledError:
        return await reply.edit("`Cancelled....`")
    except BaseException:
        func_out = str(traceback.format_exc())
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    output = codeErr.getvalue().strip() or codeOut.getvalue().strip()
    if func_out is not None:
        output = f"{output}\n\n{func_out}".strip()
    elif not output and "-s" in message.flags:
        await reply.delete()
        return
    if "-s" in message.flags:
        output = f">> `{output}`"
    else:
        output = f"```python\n> {code}```\n\n>> `{output}`"
    await reply.edit(
        output,
        name="exec.txt",
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )


if Config.DEV_MODE:
    Config.CMD_DICT["py"] = Config.CMD(
        func=executor, path=inspect.stack()[0][1], doc=executor.__doc__
    )
