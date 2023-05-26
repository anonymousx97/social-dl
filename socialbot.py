"""

* socialbot.py Main Logic file of Bot.

MIT License

Copyright (c) 2023 Ryuk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import asyncio
import base64
import glob
import json
import os
import shutil
import sys
import time
import traceback
from io import StringIO
from urllib.parse import urlparse as url_p

import aiohttp
import yt_dlp
from aiohttp_retry import ExponentialRetry, RetryClient
from dotenv import load_dotenv
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatType, ParseMode
from pyrogram.errors import MediaEmpty, PhotoSaveFileInvalid, WebpageCurlFailed
from pyrogram.handlers import MessageHandler
from pyrogram.types import InputMediaPhoto, InputMediaVideo, Message
from wget import download

if os.path.isfile("config.env"):
    load_dotenv("config.env")

bot = Client(
    name="bot",
    session_string=os.environ.get("STRING_SESSION"),
    api_id=os.environ.get("API_ID"),
    api_hash=os.environ.get("API_HASH"),
    in_memory=True,
    parse_mode=ParseMode.DEFAULT,
)

LOG_CHAT = os.environ.get("LOG")

if LOG_CHAT is None:
    print("Enter log channel id in config")
    exit()

USERS = json.loads(os.environ.get("USERS"))

TRIGGER = os.environ.get("TRIGGER")


# Download Section

# Gallery-dl for all types of media

async def gallery_dl(url:str, caption:str, ,doc:bool=false):
    download_dir = f"downloads/{time.time()}"
    await run_shell_cmd(f"gallery-dl -q -D {download_dir} '{url}'")
    files = glob.glob(f"{download_dir}/*")
    if not files:
        return "failed"
    ret_dict = {"path": download_dir, "caption": caption}
    if doc:
        ret_dict['media']=files

    # If more than 1 file return grouped media
    elif len(files) > 1:
        grouped_images, grouped_videos, animations = [], [], []
        for file in files:
            if file.endswith((".png", ".jpg", ".jpeg",".webp")):
                if file.endswith(".webp"):
                    os.rename(file,file+".png")
                    file = file+ ".png"
                grouped_images.append(InputMediaPhoto(file, caption=caption))
            elif file.endswith((".mp4", ".mkv", ".webm")):
                has_audio = await check_audio(file)
                if not has_audio:
                    animations.append(file)
                else:
                    grouped_videos.append(InputMediaVideo(file, caption=caption))

        # Limit 5 posts per list to avoid TG's flood system
        group_list = [
        grouped_images[imgs : imgs + 5] for imgs in range(0, len(grouped_images), 5)
        ] + [grouped_videos[vids : vids + 5] for vids in range(0, len(grouped_videos), 5)
        ] + animations

        # Final output of group_list = [ [1,2,3,4,5], [6,7,8,9,10] ]

        ret_dict.update({"is_grouped": True,"media": group_list})

    # Otherwise return single after renaming to proper extension coz TG converts webp to sticker
    else:
        file = files[0]
        ret_dict['media'] = file
        if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            ret_dict["is_image"] = True
            if file.lower().endswith(".webp"):
                os.rename(file, file + ".jpg")
                ret_dict.update({"media": down_load + ".jpg"})
        elif file.lower().endswith((".mkv", ".mp4", ".webm")):
            ret_dict.update({"is_video": True, "thumb": await take_ss(video=file, path=download_dir)})
        elif file.lower().endswith(".gif"):
            ret_dict.update({"is_animation": True})
    return ret_dict


# YT-DLP for videos from multiple sites
async def yt_dl(url: str, caption: str, doc:bool=False):
    path = "downloads/" + str(time.time())
    video = f"{path}/v.mp4"
    _opts = {
        "outtmpl": video,
        "ignoreerrors": True,
        "ignore_no_formats_error": True,
        "quiet": True,
        "logger": FakeLogger(),
    }
    if "shorts" in url:
        _opts.update({"format": "bv[ext=mp4][res=480]+ba[ext=m4a]/b[ext=mp4]"})
    else:
        _opts.update({"format": "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"})
    data = "failed"
    try:
        await asyncio.to_thread(yt_dlp.YoutubeDL(_opts).download, url)
        if os.path.isfile(video):
            data = {
                "path": path,
                "is_video": True,
                "media": video,
                "thumb": await take_ss(video=video, path=path),
                "caption": caption,
            }
    except BaseException:
        pass
    return data


# To disable YT-DLP logging
class FakeLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass



# Thumbnail
async def take_ss(video: str, path: str):
    await run_shell_cmd(f'''ffmpeg -hide_banner -loglevel error -ss 0.1 -i "{video}" -vframes 1 "{path}/i.png"''')
    if os.path.isfile(path + "/i.png"):
        return path + "/i.png"

# Check if it's a video or gif
async def check_audio(file):
    result = await run_shell_cmd(f"ffprobe -v error -show_entries format=nb_streams -of default=noprint_wrappers=1:nokey=1 {file}")
    return int(result.get("stdout", 0)) - 1


async def run_shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    return {"stdout": stdout.decode("utf-8"), "stderr": stderr.decode("utf-8")}


# BOT Section

@bot.on_edited_message(filters.command(commands="dl", prefixes=TRIGGER) & filters.user(USERS))
@bot.on_message(filters.command(commands="dl", prefixes=TRIGGER) & filters.user(USERS))
async def dl(bot, message: Message):
    parsed = MESSAGE_PARSER(message)
    if not parsed.coro_:
        return
    status = "failed"
    msg_ = await bot.send_message(chat_id=message.chat.id, text="`trying to download...`")
    for coroutine_ in parsed.coro_:
        media_dict = await coroutine_
        if isinstance(media_dict, dict) and "media" in media_dict:
            status = await send_media(message=message, data=media_dict, doc=parsed.doc, caption=parsed.caption)
    if status == "failed":
        return await msg_.edit(f"Media Download Failed.")
    await message.delete()
    await msg_.delete()


# Parse Message text and return coroutine for matched links
class MESSAGE_PARSER:
    def __init__(self, message):
        self.text_list = message.text.split()
        self.flags = [i for i in self.text_list if i.startswith("-")]
        self.sender = message.author_signature or (user.first_name if (user := message.from_user) else "")
        self.caption = f"Shared by : {self.sender}"
        self.doc = "-d" in self.flags
        self.coro_ = []
        self.match_links()

    # Thanks Jeel Patel [TG @jeelpatel231] for url map concept.
    def match_links(self):
        url_map = {
            "tiktok.com": yt_dl,
            "www.instagram.com": gallery_dl,
            "youtube.com/shorts": yt_dl,
            "twitter.com": gallery_dl,
            "www.reddit.com": gallery_dl,
        }
        for link in self.text_list:
            if (match := url_map.get(url_p(link).netloc)):
                self.coro_.append(match(url=link,doc=self.doc, caption=self.caption))
            else:
                for key, val in url_map.items():
                    if key in link:
                        self.coro_.append(val(url=link,doc=self.doc, caption=self.caption))



# Send media back
async def send_media(message: Message, data: dict, caption: str, doc: bool = False):
    reply = message.reply_to_message
    reply_id = reply.id if reply else None
    media = data.get("media")
    thumb = data.get("thumb", None)
    caption = data.get("caption", "")
    is_image, is_video, is_animation, is_grouped = (data.get("is_image"), data.get("is_video"), data.get("is_animation"), data.get("is_grouped"))
    status = "failed"
    args_ = {"chat_id": message.chat.id, "reply_to_message_id": reply_id}
    if isinstance(media, list):
        for vv in media:
            try:
                if isinstance(vv, list):
                    status = await bot.send_media_group(**args_, media=vv)
                    await asyncio.sleep(2)
                elif doc:
                    status = await bot.send_document(**args_, caption=caption, document=vv, force_document=True)
                else:
                    status = await bot.send_animation(**args_, caption=caption, animation=vv, unsave=True)
            except Exception:
                await bot.send_message(chat_id=LOG_CHAT, text=str(traceback.format_exc()))
    else:
        args_.update({"caption": caption})
        try:
            if is_image:
                status = await bot.send_photo(**args_, photo=media)
            elif is_video:
                status = await bot.send_video(**args_, video=media, thumb=thumb)
            elif is_animation:
                status = await bot.send_animation(**args_, animation=media, unsave=True)
            else:
                status = await bot.send_document(**args_, document=media, force_document=True)
        except PhotoSaveFileInvalid:
            await bot.send_document(**args_, document=media, force_document=True)
        except (MediaEmpty, WebpageCurlFailed, ValueError):
            pass
    if os.path.exists(str(data["path"])):
        shutil.rmtree(str(data["path"]))
    if status != "failed":
        return "done"
    return status



@bot.on_edited_message(filters.command(commands="bot", prefixes=TRIGGER) & filters.user(USERS))
@bot.on_message(filters.command(commands="bot", prefixes=TRIGGER) & filters.user(USERS))
async def multi_func(bot, message: Message):
    rw_message = message.text.split()
    try:
        # Restart
        if "restart" in rw_message:
            await SESSION.close()
            await RETRY_CLIENT.close()
            os.execl(sys.executable, sys.executable, __file__)

        # Get chat / channel id
        elif "ids" in rw_message:
            if (reply := message.reply_to_message):
                ids = ""
                reply_forward = reply.forward_from_chat
                reply_user = reply.from_user
                ids += f"Chat : `{reply.chat.id}`\n"
                if reply_forward:
                    ids += f"Replied {'Channel' if reply_forward.type == ChatType.CHANNEL else 'Chat'} : `{reply_forward.id}`\n"
                if reply_user:
                    ids += f"User : {reply.from_user.id}"
            else:
                ids = f"Chat :`{message.chat.id}`"
            await message.reply(ids)

        # Update Auto-DL chats
        elif "update" in rw_message:
            bot.remove_handler(*HANDLER_)
            await add_h()
            await message.reply("Chat list refreshed")

        # Join a chat
        elif "join" in rw_message:
            if len(rw_message) > 2:
                try:
                    await bot.join_chat(rw_message[-1])
                except KeyError:
                    await bot.join_chat(os.path.basename(rw_message[-1]).strip())
                except Exception as e:
                    return await message.reply(str(e))
                await message.reply("Joined")
        # Leave a chat
        elif "leave" in rw_message:
            if len(rw_message) == 3:
                chat = rw_message[-1]
            else:
                chat = message.chat.id
            await bot.leave_chat(chat)

        else:
            await message.reply("Social-DL is running")
    except Exception:
        await bot.send_message(chat_id=LOG_CHAT, text=str(traceback.format_exc()))


# Delete replied and command message
@bot.on_message(filters.command(commands="del", prefixes=TRIGGER) & filters.user(USERS))
async def delete_message(bot, message: Message):
    reply = message.reply_to_message
    await message.delete()
    if reply:
        await reply.delete()


# Delete Multiple messages from replied to command.
@bot.on_message(filters.command(commands="purge", prefixes=TRIGGER) & filters.user(USERS))
async def purge_(bot, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply("reply to a message")
    start_message = reply.id
    end_message = message.id
    messages = [end_message] + [i for i in range(int(start_message), int(end_message))]
    await bot.delete_messages(chat_id=message.chat.id, message_ids=messages, revoke=True)


if os.environ.get("DEV_MODE") == "yes":
    # Run shell commands
    @bot.on_edited_message(filters.command(commands="sh", prefixes=TRIGGER) & filters.user(USERS))
    @bot.on_message(filters.command(commands="sh", prefixes=TRIGGER) & filters.user(USERS))
    async def run_cmd(bot, message: Message):
        cmd = message.text.replace(f"{TRIGGER}sh ", "").strip()
        status_ = await message.reply("executing...")
        proc = await run_shell_cmd(cmd)
        output = f"${cmd}"
        if (stdout := proc.get("stdout")):
            output += f"""\n\n**Output:**\n\n`{stdout}`"""
        if (stderr := proc.get("stderr")):
            output += f"""\n\n**Error:**\n\n`{stderr}`"""
        await status_.edit(output,parse_mode=ParseMode.MARKDOWN)


    # Run Python code
    @bot.on_edited_message(
        filters.command(commands="exec", prefixes=TRIGGER) & filters.user(USERS)
    )
    @bot.on_message(
        filters.command(commands="exec", prefixes=TRIGGER) & filters.user(USERS)
    )
    async def executor_(bot, message):
        code = message.text.replace(f"{TRIGGER}exec","").strip()
        if not code:
            return await message.reply("exec Jo mama?")
        reply = await message.reply("executing")
        sys.stdout = codeOut = StringIO() 
        sys.stderr = codeErr = StringIO()
        # Indent code as per proper python syntax 
        formatted_code = "".join(["\n    "+i for i in code.split("\n")])
        try:
            # Create and initialise the function
            exec(f"async def exec_(bot, message):{formatted_code}")
            func_out = await locals().get("exec_")(bot, message)
        except Exception:
            func_out = str(traceback.format_exc())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        output = codeOut.getvalue().strip() or codeErr.getvalue().strip() or func_out or ""
        await reply.edit(f"> `{code}`\n\n>> `{output}`",parse_mode=ParseMode.MARKDOWN)


# Add Auto-DL regex Handler
async def add_h():
    message_id = os.environ.get("MESSAGE")
    if message_id is None:
        print("\nEnter Message id in config.\n")
        return 1
    try:
        msg = (await bot.get_messages(int(LOG_CHAT), int(message_id))).text
    except PeerIdInvalid:
        print("\nLog channel not found.\nCheck the variable for mistakes")
        return 1
    if msg is None:
        print("\nMessage not found\nCheck variable for mistakes\n")
        return 1
    try:
        chats_list = [int(i) for i in msg.split()]
    except ValueError:
        print("\nThe message id is wrong. \nOr \nChat id message contains letters\nonly numerical ids are allowed.\n")
        return 1
    social_handler = bot.add_handler(
        MessageHandler(dl,(filters.regex(r"^http*")& filters.chat(chats_list))),group=1)
    globals().update({"HANDLER_":social_handler})


# Start the bot and wait idle without blocking the main loop
async def boot():
    check_handlers = await add_h()
    msg = "#Social-dl\nStarted\n"
    if check_handlers == 1:
        msg += "\n* Running in command only mode. *"
    print(msg)
    await bot.send_message(chat_id=int(LOG_CHAT), text="#Social-dl\n__Started__")
    globals().update({"SESSION":aiohttp.ClientSession()})
    globals().update({"RETRY_CLIENT":RetryClient(client_session=SESSION, retry_for_statuses={408, 504}, retry_options=ExponentialRetry(attempts=1))})
    await idle()


# Start only bot when file is called directly.
if __name__ == "__main__":
    bot.start()
    bot.run(boot())
