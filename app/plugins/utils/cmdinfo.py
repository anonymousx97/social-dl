import os

from app import BOT, Config, Message, bot


@bot.add_cmd(cmd="ci")
async def cmd_info(bot: BOT, message: Message):
    """
    CMD: CI (CMD INFO)
    INFO: Get Github File URL of a Command.
    USAGE: .ci ci
    """
    cmd = message.flt_input
    if not cmd or cmd not in Config.CMD_DICT.keys():
        await message.reply("Give a valid cmd.", del_in=5)
        return
    cmd_path = Config.CMD_DICT[cmd].path
    plugin_path = os.path.relpath(cmd_path, os.curdir)
    repo = Config.REPO.remotes.origin.url
    branch = Config.REPO.active_branch
    remote_url = os.path.join(str(repo), "blob", str(branch), plugin_path)
    resp_str = (
        f"<pre language=bash>CMD={cmd}"
        f"\nLocal_Path={cmd_path}</pre>"
        f"\nLink: <a href='{remote_url}'>Github</a>"
    )
    await message.reply(resp_str, disable_web_page_preview=True)
