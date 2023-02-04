import asyncio
import base64
import json
import os
import shutil
import sys
import time
import traceback
from subprocess import call

import aiohttp
import yt_dlp
from dotenv import load_dotenv
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatType
from pyrogram.errors import MediaEmpty, PhotoSaveFileInvalid, WebpageCurlFailed, PeerIdInvalid
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
)
log_chat = os.environ.get("LOG")
if log_chat == None:
    print("Enter log channel id in config")
    exit()
chat_list = []
handler_ = []
users = json.loads(os.environ.get("USERS"))
trigger = os.environ.get("TRIGGER")
e_json = base64.b64decode("Lz9fX2E9MSZfX2Q9MQ==").decode("utf-8")


@bot.on_message(filters.command(commands="bot", prefixes=trigger) & filters.user(users))
async def multi_func(bot, message: Message):
    rw_message = message.text.split()
    try:
        if "restart" in rw_message:
            """Restart bot"""
            os.execl(sys.executable, sys.executable, __file__)

        elif "ids" in rw_message:
            """Get chat / channel id"""
            ids = ""
            reply = message.reply_to_message
            if reply:
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

        elif "update" in rw_message:
            """Update Auto-DL chats"""
            for i in handler_:
                bot.remove_handler(*i)
            await add_h()
            await message.reply("Chat list refreshed")

        elif "join" in rw_message:
            """Join a Chat"""
            if len(rw_message) > 2:
                try:
                    await bot.join_chat(rw_message[-1])
                except KeyError:
                    await bot.join_chat(rw_message[-1].split()[-1])
                except Exception as e:
                    return await message.reply(str(e))
                await message.reply("Joined")

        elif "leave" in rw_message:
            """Leave a Chat"""
            if len(rw_message) == 3:
                chat = rw_message[-1]
            else:
                chat = message.chat.id
            await bot.leave_chat(chat)

        else:
            await message.reply("Social-DL is running.")
    except Exception:
        await bot.send_message(chat_id=log_chat, text=str(traceback.format_exc()))


@bot.on_message(
    filters.command(commands="term", prefixes=trigger) & filters.user(users)
)
async def run_cmd(bot, message: Message):
    """Function to run shell commands"""
    cmd = message.text.replace("+term", "")
    status_ = await message.reply("executing...")
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode is not None:
        output = f"${cmd}"
        if stdout:
            output += f"\n\n**Output:**\n\n`{stdout.decode('utf-8')}`"
        if stderr:
            output += f"\n\n**Error:**\n\n`{stderr.decode('utf-8')}`"
        await status_.edit(output)


@bot.on_message(filters.command(commands="del", prefixes=trigger) & filters.user(users))
async def delete_message(bot, message: Message):
    """Delete Messages"""
    reply = message.reply_to_message
    await message.delete()
    if reply:
        await reply.delete()


@bot.on_message(filters.command(commands="dl", prefixes=trigger) & filters.user(users))
async def dl(bot, message: Message):
    """ The main Logic Function to download media """
    response = await bot.send_message(message.chat.id, "`trying to download...`")
    rw_message = message.text.split()
    curse_ = ""
    caption = "Shared by : "
    if message.sender_chat:
        caption += message.author_signature
    else:
        caption += message.from_user.first_name
    check_dl = "failed"
    if "-d" in rw_message:
        doc = True
    else:
        doc = False
    for i in rw_message:
        if i.startswith("https://www.instagram.com/"):
            check_dl = await iyt_dl(url=i)
            curse_ = "#FuckInstagram"
            if check_dl == "failed":
                check_dl = await json_dl(iurl=i, caption=caption, doc=doc)

        if "twitter.com" in i or "https://youtube.com/shorts" in i or "tiktok.com" in i:
            check_dl = await iyt_dl(url=i)

        if isinstance(check_dl, dict):
            """Send Media if response from check dl contains data dict"""
            if isinstance(check_dl["media"], list):
                for data_ in check_dl["media"]:
                    if isinstance(vv, list):
                        """Send Grouped Media if data contains a list made of smaller lists of 5 medias"""
                        await bot.send_media_group(
                            message.chat.id,
                            media=data_,
                            reply_to_message_id=message.reply_to_message.id
                            if message.reply_to_message
                            else None,
                        )
                        await asyncio.sleep(3)
                    else:
                        """Send Document if data is list of media files"""
                        await bot.send_document(
                            message.chat.id,
                            document=data_,
                            caption=caption,
                            reply_to_message_id=message.reply_to_message.id
                            if message.reply_to_message
                            else None,
                        )
            """ If media isn't a list then it's a single file to be sent """
            if isinstance(check_dl["media"], str):
                if doc:
                    await bot.send_document(
                        message.chat.id,
                        document=check_dl["media"],
                        caption=caption,
                        reply_to_message_id=message.reply_to_message.id
                        if message.reply_to_message
                        else None,
                    )
                else:
                    if check_dl["type"] == "img":
                        await bot.send_photo(
                            message.chat.id,
                            photo=check_dl["media"],
                            caption=caption,
                            reply_to_message_id=message.reply_to_message.id
                            if message.reply_to_message
                            else None,
                        )
                    if check_dl["type"] == "vid":
                        try:
                            await bot.send_video(
                                message.chat.id,
                                video=check_dl["media"],
                                caption=caption,
                                thumb=check_dl["thumb"]
                                if os.path.isfile(check_dl["thumb"])
                                else None,
                                reply_to_message_id=message.reply_to_message.id
                                if message.reply_to_message
                                else None,
                            )
                        except (MediaEmpty, WebpageCurlFailed):
                            pass
            if os.path.exists(str(check_dl["path"])):
                shutil.rmtree(str(check_dl["path"]))
            check_dl = "done"
    if check_dl == "failed":
        await response.edit(f"Media Download Failed.\n{curse_}")
    if check_dl == "done":
        await message.delete()
        await response.delete()


async def iyt_dl(url: str):
    """Stop handling post url because this only downloads Videos and post might contain images"""
    if url.startswith("https://www.instagram.com/p/"):
        return "failed"
    path_ = time.time()
    video = f"{path_}/v.mp4"
    thumb = f"{path_}/i.png"
    _opts = {
        "outtmpl": video,
        "ignoreerrors": True,
        "ignore_no_formats_error": True,
        "format": "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
        "quiet": True,
        "logger": FakeLogger(),
    }
    return_val = "failed"
    try:
        yt_dlp.YoutubeDL(_opts).download(url)
        if os.path.isfile(video):
            call(
                f'''ffmpeg -hide_banner -loglevel error -ss 0.1 -i "{video}" -vframes 1 "{thumb}"''',
                shell=True,
            )
            return_val = {
                "path": str(path_),
                "type": "vid",
                "media": video,
                "thumb": thumb,
            }
    except BaseException:
        pass
    return return_val


async def json_dl(iurl: str, doc: bool, caption: str):
    link = iurl.split("/?")[0] + e_json
    async with (aiohttp.ClientSession() as csession, csession.get(link, timeout=10) as session):
        try:
            session_resp = await session.text()
            rjson = json.loads(session_resp)
        except json.decoder.JSONDecodeError:
            return "failed"
        if "require_login" in rjson:
            return "failed"

    return_val = "failed"
    if "graphql" in rjson:
        try:
            url = rjson["graphql"]["shortcode_media"]
            d_dir = f"downloads/{time.time()}"
            os.makedirs(d_dir)
            if url["__typename"] == "GraphVideo":
                url_ = url["video_url"]
                wget_x = download(url_, d_dir)
                call(
                    f'''ffmpeg -hide_banner -loglevel error -ss 0.1 -i "{wget_x}" -vframes 1 "{d_dir}/i.png"''',
                    shell=True,
                )
                return_val = { "path": d_dir, "type": "vid", "media": wget_x, "thumb": d_dir + "/i.png" }

            if url["__typename"] == "GraphImage":
                url_ = url["display_url"]
                wget_x = download(url_, d_dir + "/i.jpg")
                return_val = { "path": d_dir, "type": "img", "media": wget_x, "thumb": "" }

            if url["__typename"] == "GraphSidecar":
                doc_list = []
                vlist = []
                vlist2 = []
                plist = []
                plist2 = []
                for i in url["edge_sidecar_to_children"]["edges"]:
                    if i["node"]["__typename"] == "GraphImage":
                        url_ = i["node"]["display_url"]
                        wget_x = download(url_, d_dir)
                        if wget_x.endswith(".webp"):
                            os.rename(wget_x, wget_x + ".jpg")
                            wget_x = wget_x + ".jpg"
                        if doc:
                            doc_list.append(wget_x)
                        else:
                            if len(plist) >= 5:
                                plist2.append(InputMediaPhoto(media=wget_x, caption=caption))
                            else:
                                plist.append(InputMediaPhoto(media=wget_x, caption=caption))
                    if i["node"]["__typename"] == "GraphVideo":
                        url_ = i["node"]["video_url"]
                        wget_x = download(url_, d_dir)
                        if doc:
                            doc_list.append(wget_x)
                        else:
                            if len(vlist) >= 5:
                                vlist2.append(InputMediaVideo(media=wget_x, caption=caption))
                            else:
                                vlist.append(InputMediaVideo(media=wget_x, caption=caption))
                if doc:
                    return_val = {"path": d_dir, "media": doc_list}
                else:
                    return_val = {
                        "path": d_dir,
                        "media": [
                            zz for zz in [plist, plist2, vlist, vlist2] if len(zz) > 0
                        ],
                    }
        except Exception:
            await bot.send_message(chat_id=log_chat, text=str(traceback.format_exc()))
    return return_val


@bot.on_message(filters.command(commands="rdl", prefixes=trigger) & filters.user(users))
async def reddit_dl(bot, message: Message):
    ext = None
    del_link = True
    rw_message = message.text.split()
    response = await bot.send_message(
        chat_id=message.chat.id, text="Trying to download..."
    )
    if message.sender_chat:
        sender_ = message.author_signature
    else:
        sender_ = message.from_user.first_name
    for link_ in rw_message:
        if link_.startswith("https://www.reddit.com"):
            link = link_.split("/?")[0] + ".json?limit=1"
            headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_7 rv:5.0; en-US) AppleWebKit/533.31.5 (KHTML, like Gecko) Version/4.0 Safari/533.31.5",
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(link, headers=headers) as ss:
                        session_response = await ss.json()
                json_ = session_response[0]["data"]["children"][0]["data"]
                check_ = json_["secure_media"]
                title_ = json_["title"]
                subr = json_["subreddit_name_prefixed"]
                caption = f"__{subr}:__\n**{title_}**\n\nShared by : {sender_}"
                d_dir = str(time.time())
                os.mkdir(d_dir)
                if isinstance(check_, dict):
                    v = f"{d_dir}/v.mp4"
                    t = f"{d_dir}/i.png"
                    if "oembed" in check_:
                        vid_url = json_["preview"]["reddit_video_preview"]["fallback_url"]
                        await bot.send_animation(
                            chat_id=message.chat.id,
                            animation=vid_url,
                            unsave=True,
                            caption=caption,
                        )
                    else:
                        vid_url = check_["reddit_video"]["hls_url"]
                        call(
                            f'ffmpeg -hide_banner -loglevel error -i "{vid_url.strip()}" -c copy {v}',
                            shell=True,
                        )
                        call(
                            f'''ffmpeg -ss 0.1 -i "{v}" -vframes 1 "{t}"''', shell=True
                        )
                        await message.reply_video(v, caption=caption, thumb=t)
                else:
                    media_ = json_["url_overridden_by_dest"]
                    try:
                        if media_.strip().endswith(".gif"):
                            ext = ".gif"
                            await bot.send_animation(
                                chat_id=message.chat.id,
                                animation=media_,
                                unsave=True,
                                caption=caption,
                            )
                        if media_.strip().endswith((".jpg", ".jpeg", ".png", ".webp")):
                            ext = ".png"
                            await message.reply_photo(media_, caption=caption)
                    except (MediaEmpty, WebpageCurlFailed):
                        download(media_, f"{d_dir}/i{ext}")
                        if ext == ".gif":
                            await bot.send_animation(
                                chat_id=message.chat.id,
                                animation=f"{d_dir}/i.gif",
                                unsave=True,
                                caption=caption,
                            )
                        else:
                            try:
                                await message.reply_photo(f"{d_dir}/i.png", caption=caption)
                            except PhotoSaveFileInvalid:
                                await message.reply_document(document=f"{d_dir}/i.png", caption=caption)
                if os.path.exists(str(d_dir)):
                    shutil.rmtree(str(d_dir))
            except Exception:
                del_link = False
                await bot.send_message(chat_id=log_chat, text=str(traceback.format_exc()))
                await response.edit("Link doesn't contain any media or is restricted\nTip: Make sure you are sending original post url and not an embedded post.")
            continue
    if del_link:
        await message.delete()
        await response.delete()


class FakeLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


async def add_h():
    message_id = os.environ.get("MESSAGE")
    if message_id == None:
        print("Enter Message id in config.\n")
        return 1
    try:
        msg = (await bot.get_messages(int(log_chat), int(message_id))).text
    except PeerIdInvalid:
        print("Log channel not found.\nCheck the variable for mistakes")
        return 1
    chat_list.clear()
    if msg == None:
        print("Message not found\nCheck variable for mistakes\n")
        return 1
    try:
        chats_list = [int(i) for i in msg.split()]
    except ValueError:
        print("Chat id message contains letters\nonly numerical ids are allowed.\nOr the message id is wrong.\n")
        return 1
    chat_list.extend(chats_list)
    social_handler = bot.add_handler(
        MessageHandler(
            dl,
            (
                (
                    filters.regex(r"^https://www.instagram.com/*")
                    | filters.regex(r"^https://youtube.com/shorts/*")
                    | filters.regex(r"^https://twitter.com/*")
                    | filters.regex(r"^https://vm.tiktok.com/*")
                )
                & filters.chat(chat_list)
            ),
        ),
        group=1,
    )
    reddit_handler = bot.add_handler(
        MessageHandler(
            reddit_dl,
            (filters.regex(r"^https://www.reddit.com/*") & filters.chat(chat_list)),
        ),
        group=2,
    )
    handler_.extend([social_handler, reddit_handler])


async def boot():
    check_handlers = await add_h()
    msg = "#Social-dl\nStarted\n"
    if check_handlers == 1:
        msg += "Running in command only mode."
        print(msg)
    await bot.send_message(chat_id=int(log_chat), text=msg)
    await idle()


if __name__ == "__main__":
    bot.start()
    bot.run(boot())
