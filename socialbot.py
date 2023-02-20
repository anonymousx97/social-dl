import asyncio
import base64
import glob
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
from pyrogram.errors import MediaEmpty, PeerIdInvalid, PhotoSaveFileInvalid, WebpageCurlFailed
from pyrogram.handlers import MessageHandler
from pyrogram.types import InputMediaPhoto, InputMediaVideo, Message
from wget import download

if os.path.isfile("config.env"):
    load_dotenv("config.env")

bot = Client(name="bot", session_string=os.environ.get("STRING_SESSION"), api_id=os.environ.get("API_ID"), api_hash=os.environ.get("API_HASH"))
log_chat = os.environ.get("LOG")
if log_chat is None:
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


@bot.on_message(filters.command(commands="term", prefixes=trigger) & filters.user(users))
async def run_cmd(bot, message: Message):
    """Function to run shell commands"""
    cmd = message.text.replace("+term", "")
    status_ = await message.reply("executing...")
    process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
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
    """The main Logic Function to download media"""
    rw_message = message.text.split()
    reply = message.reply_to_message
    reply_id = reply.id if reply else None
    sender_ = message.author_signature or message.from_user.first_name or ""
    response = await bot.send_message(message.chat.id, "`trying to download...`")
    curse_ = ""
    caption = f"Shared by : {sender_}"
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
        elif "twitter.com" in i or "https://youtube.com/shorts" in i or "tiktok.com" in i:
            check_dl = await iyt_dl(url=i)
        elif "www.reddit.com" in i:
            check_dl = await reddit_dl(url_=i, doc=doc, sender_=sender_)
            curse_ = "Link doesn't contain any media or is restricted\nTip: Make sure you are sending original post url and not an embedded post."
        else:
            pass
        if isinstance(check_dl, dict):
            if isinstance(check_dl["media"], list):
                for vv in check_dl["media"]:
                    if isinstance(vv, list):
                        await bot.send_media_group(message.chat.id, media=vv, reply_to_message_id=reply_id)
                        await asyncio.sleep(3)
                    else:
                        await bot.send_document(message.chat.id, document=vv, caption=check_dl["caption"] + caption, reply_to_message_id=reply_id, force_document=True)
            else:
                if doc:
                    await bot.send_document(message.chat.id, document=check_dl["media"], caption=check_dl["caption"] + caption, reply_to_message_id=reply_id, force_document=True)
                else:
                    try:
                        if check_dl["type"] == "img":
                            await bot.send_photo(message.chat.id, photo=check_dl["media"], caption=check_dl["caption"] + caption, reply_to_message_id=reply_id)
                        elif check_dl["type"] == "vid":
                            await bot.send_video(message.chat.id, video=check_dl["media"], caption=check_dl["caption"] + caption, thumb=check_dl["thumb"], reply_to_message_id=reply_id)
                        else:
                            await bot.send_animation(message.chat.id, animation=check_dl["media"], caption=check_dl["caption"] + caption, reply_to_message_id=reply_id, unsave=True)
                    except PhotoSaveFileInvalid:
                        await bot.send_document(message.chat.id, document=check_dl["media"], caption=check_dl["caption"] + caption, reply_to_message_id=reply_id)
                    except (MediaEmpty, WebpageCurlFailed, ValueError):
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
    if not url.startswith("https://www.instagram.com/reel/"):
        return "failed"
    path_ = time.time()
    video = f"{path_}/v.mp4"
    thumb = f"{path_}/i.png"
    _opts = {"outtmpl": video, "ignoreerrors": True, "ignore_no_formats_error": True, "format": "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]", "quiet": True, "logger": FakeLogger()}
    return_val = "failed"
    try:
        yt_dlp.YoutubeDL(_opts).download(url)
        if os.path.isfile(video):
            call(f'''ffmpeg -hide_banner -loglevel error -ss 0.1 -i "{video}" -vframes 1 "{thumb}"''', shell=True)
            return_val = {"path": str(path_), "type": "vid", "media": video, "thumb": thumb if os.path.isfile(thumb) else None, "caption": ""}
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
                call(f'''ffmpeg -hide_banner -loglevel error -ss 0.1 -i "{wget_x}" -vframes 1 "{d_dir}/i.png"''', shell=True)
                return_val = {"path": d_dir, "type": "vid", "media": wget_x, "thumb": d_dir + "/i.png", "caption": ""}

            if url["__typename"] == "GraphImage":
                url_ = url["display_url"]
                wget_x = download(url_, d_dir + "/i.jpg")
                return_val = {"path": d_dir, "type": "img", "media": wget_x, "thumb": None, "caption": ""}

            if url["__typename"] == "GraphSidecar":
                url_list = []
                for i in url["edge_sidecar_to_children"]["edges"]:
                    if i["node"]["__typename"] == "GraphImage":
                        url_list.append(i["node"]["display_url"])
                    if i["node"]["__typename"] == "GraphVideo":
                        url_list.append(i["node"]["video_url"])
                downloads = await async_download(urls=url_list, path=d_dir, doc=doc, caption=caption + "\n..")
                return_val = {"path": d_dir, "media": downloads}
        except Exception:
            await bot.send_message(chat_id=log_chat, text=str(traceback.format_exc()))
    return return_val


async def reddit_dl(bot, message: Message):
    link = url_.split("/?")[0] + ".json?limit=1"
    headers = {"user-agent": "Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_7 rv:5.0; en-US) AppleWebKit/533.31.5 (KHTML, like Gecko) Version/4.0 Safari/533.31.5"}
    return_val = "failed"
    try:
        async with (aiohttp.ClientSession() as session, session.get(link, headers=headers) as ss):
            response = await ss.json()
        json_ = response[0]["data"]["children"][0]["data"]
        caption = f'__{json_["subreddit_name_prefixed"]}:__\n**{json_["title"]}**\n\n'
        d_dir = str(time.time())
        os.mkdir(d_dir)
        is_vid, is_gallery = json_.get("is_video"), json_.get("is_gallery")

        if is_vid:
            video = f"{d_dir}/v.mp4"
            thumb = f"{d_dir}/i.png"
            vid_url = json_["secure_media"]["reddit_video"]["hls_url"]
            call(f'ffmpeg -hide_banner -loglevel error -i "{vid_url.strip()}" -c copy {video}', shell=True)
            call(f'''ffmpeg -hide_banner -loglevel error -ss 0.1 -i "{video}" -vframes 1 "{thumb}"''', shell=True)
            return_val = {"path": d_dir, "type": "vid", "media": video, "thumb": thumb, "caption": caption}

        elif is_gallery:
            grouped_media_urls = [f'https://i.redd.it/{i["media_id"]}.jpg' for i in json_["gallery_data"]["items"]]
            downloads = await async_download(urls=grouped_media_urls, path=d_dir, doc=doc, caption=caption + f"Shared by : {sender_}")
            return_val = {"path": d_dir, "media": downloads}

        else:
            media_ = json_["url_overridden_by_dest"].strip()
            if media_.endswith((".jpg", ".jpeg", ".png", ".webp")):
                img = download(media_, d_dir)
                return_val = {"path": d_dir, "type": "img", "media": img, "thumb": None, "caption": caption}
            elif media_.endswith(".gif"):
                gif = download(media_, d_dir)
                return_val = {"path": d_dir, "type": "animation", "media": gif, "thumb": None, "caption": caption}
            else:
                gif_url = json_.get("preview", {}).get("reddit_video_preview", {}).get("fallback_url")
                if gif_url:
                    gif = download(gif_url, d_dir)
                    return_val = {"path": d_dir, "type": "animation", "media": gif, "thumb": None, "caption": caption}

    except Exception:
        await bot.send_message(chat_id=log_chat, text=str(traceback.format_exc()))
    return return_val


async def async_download(urls: list, path: str, doc: bool = False, caption: str = ""):
    down_loads = await asyncio.gather(*[asyncio.to_thread(download, url, path) for url in urls])
    if doc:
        return down_loads
    [os.rename(file, file + ".png") for file in glob.glob(f"{path}/*.webp")]
    files = glob.glob(f"{path}/*")
    grouped_images = [InputMediaPhoto(img, caption=caption) for img in files if img.endswith((".png", ".jpg", ".jpeg"))]
    grouped_videos = [InputMediaVideo(vid, caption=caption) for vid in files if vid.endswith((".mp4", ".mkv", ".webm"))]
    return_list = [grouped_images[imgs : imgs + 5] for imgs in range(0, len(grouped_images), 5)] + [
        grouped_videos[vids : vids + 5] for vids in range(0, len(grouped_videos), 5)
    ]
    return return_list


class FakeLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


async def add_h():
    message_id = os.environ.get("MESSAGE")
    if message_id is None:
        print("Enter Message id in config.\n")
        return 1
    try:
        msg = (await bot.get_messages(int(log_chat), int(message_id))).text
    except PeerIdInvalid:
        print("Log channel not found.\nCheck the variable for mistakes")
        return 1
    chat_list.clear()
    if msg is None:
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
            dl,((
                    filters.regex(r"^https://www.instagram.com/*")
                    | filters.regex(r"^https://youtube.com/shorts/*")
                    | filters.regex(r"^https://twitter.com/*")
                    | filters.regex(r"^https://vm.tiktok.com/*")
                    | filters.regex(r"^https://www.reddit.com/*")
                ) & filters.chat(chat_list))),
        group=1,
    )
    handler_.append(social_handler)


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
