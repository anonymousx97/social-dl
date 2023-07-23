import asyncio
import sys
import traceback
from io import StringIO

from pyrogram.enums import ParseMode

from app import Config
from app.core import shell
from app.core import aiohttp_tools as aio

# Run shell commands

async def run_cmd(bot, message):
    cmd = message.input.strip()
    status_ = await message.reply("executing...")
    proc_stdout = await shell.run_shell_cmd(cmd)
    output = f"`${cmd}`\n\n`{proc_stdout}`"
    return await status_.edit(output, name="sh.txt", disable_web_page_preview=True)


# Shell but Live Output


async def live_shell(bot, message):
    cmd = message.input.strip()
    sub_process = await shell.AsyncShell.run_cmd(cmd)
    reply = await message.reply("`getting live output....`")
    output = ""
    sleep_for = 1
    while sub_process.is_not_completed:
        # Edit message only when there's new output.
        if output != sub_process.full_std:
            output = sub_process.full_std
            if len(output) <= 4096:
                await reply.edit(f"`{output}`", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
        # Reset sleep duration
        if sleep_for >= 5:
            sleep_for = 1
        # Sleep to Unblock running loop and let output reader read new
        # output.
        await asyncio.sleep(sleep_for)
        sleep_for += 1
    # If the subprocess is finished edit the message with cmd and full
    # output
    return await reply.edit(f"`$ {cmd}\n\n``{sub_process.full_std}`", name="shell.txt", disable_web_page_preview=True)


# Run Python code
async def executor_(bot, message):
    code = message.flt_input.strip()
    if not code:
        return await message.reply("exec Jo mama?")
    reply = await message.reply("executing")
    sys.stdout = codeOut = StringIO()
    sys.stderr = codeErr = StringIO()
    # Indent code as per proper python syntax
    formatted_code = "\n    ".join(code.splitlines())
    try:
        # Create and initialise the function
        exec(f"async def _exec(bot, message):\n    {formatted_code}")
        func_out = await locals().get("_exec")(bot, message)
    except BaseException:
        func_out = str(traceback.format_exc())
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    output = f"`{codeOut.getvalue().strip() or codeErr.getvalue().strip() or func_out}`"
    if "-s" not in message.flags:
        output = f"> `{code}`\n\n>>  {output}"
    return await reply.edit(output, name="exec.txt", disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)


if Config.DEV_MODE:
    Config.CMD_DICT["sh"] = run_cmd
    Config.CMD_DICT["shell"] = live_shell
    Config.CMD_DICT["exec"] = executor_
