import os
import time
from dotenv import load_dotenv
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid
import logging

logging.disable(level="NOTSET")

if os.path.isfile("config.env"):
    load_dotenv("config.env")

bot = Client(
    name="bot",
    session_string=os.environ.get("STRING_SESSION"),
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH"),
)

user_= int(os.environ.get("USER"))
chat_var = os.environ.get("MESSAGE_LINK").split("/")
chat_list = []
trigger=os.environ.get("TRIGGER")
handler_ = None


async def add_h():
  try:
    msg = (await bot.get_messages(int(chat_var[0]), int(chat_var[1]))).text
  except PeerIdInvalid:
    print("WARNING:\n  Make sure you have entered the\n  message link variable correctly\n  Check readme.md for details\n\nCurrently running on command mode.\n")
    return
    chat_list.clear()
    chat_list.extend([int(i) for i in msg.split()])
    global handler_
    handler_ = bot.add_handler(
        MessageHandler(
            dl, filters.regex("^https://www.instagram.com/*") & filters.chat(chat_list)
        ),
        group=1,
    )


async def update_h(bot, message: Message):
    bot.remove_handler(*handler_)
    await add_h()
    await message.reply("Chat list refreshed")


def boot():
    bot.start()
    bot.run(add_h())
    bot.add_handler(
        MessageHandler(dl, filters.command(commands="dl", prefixes=trigger) & filters.user([user_])), group=0
    )
    bot.add_handler(
        MessageHandler(
            update_h, filters.command(commands="update", prefixes=trigger) & filters.user([user_])
        ),
        group=2,
    )
    try:
      bot.send_message(chat_id=chat_var[0], text="#Instadl\n**Started**")
    except PeerIdInvalid:
      pass
    print("STARTED")
    idle()


def dl(bot, message: Message):
    msg_ = message.reply("`trying to download...`")
    import shutil

    m = message.text.split()
    caption = "Shared by : "
    if message.sender_chat:
        caption += message.author_signature
    else:
        caption += (
            bot.get_users(message.from_user.username or message.from_user.id)
        ).first_name
    del_link = True
    for i in m:
        if i.startswith("http"):
            try:
                link = i.split("/?")[0] + "/?__a=1&__d=dis"
                import requests
                from pyrogram.errors import FloodWait, MediaEmpty, WebpageCurlFailed
                #import fake_headers
                #h = fake_headers.Headers(browser="chrome", os="android", headers=True).generate()
                session = requests.Session()
                rurl_ = session.get(link)
                url = rurl_.json()["graphql"]["shortcode_media"]
                if url["__typename"] == "GraphVideo":
                    url_=url["video_url"]
                    message.reply_video(url_, caption=caption)
                if url["__typename"] == "GraphImage":
                    url_=url["display_url"]
                    message.reply_photo(url_, caption=caption)
                if url["__typename"] == "GraphSidecar":
                    msg_.edit("Multiple Media found.\nTrying to send all......")

                    for i in url["edge_sidecar_to_children"]["edges"]:
                        time.sleep(1)
                        if i["node"]["__typename"] == "GraphImage":
                            url_=i["node"]["display_url"]
                            message.reply_photo(
                                url_, caption=caption
                            )
                        if i["node"]["__typename"] == "GraphVideo":
                            url_=i["node"]["video_url"]
                            message.reply_video(url_, caption=caption)
            except FloodWait as f:
                time.sleep(f.value + 2)
            except (MediaEmpty, WebpageCurlFailed):
                from wget import download

                x = download(url_)
                message.reply_video(x, caption=caption)
                if os.path.isfile(x):
                    shutil.rmtree(x)
            except (ValueError, TypeError, KeyError):
                try:
                    time_ = time.time()
                    import yt_dlp

                    v = f"{time_}/v.mp4"
                    _opts = {
                        "outtmpl": v,
                        "logger": logger,
                        "ignoreerrors": True,
                        "quite":True,
                        "format": "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
                    }
                    x = yt_dlp.YoutubeDL(_opts).download(i)
                    message.reply_video(v, caption=caption)
                    shutil.rmtree(str(time_))
                except Exception as e:
                    msg_.edit(f"link not supported or private.")
                    if not str(e).startswith("Failed to decode") and len(chat_list)!=0:
                        bot.send_message(chat_id=chat_var[0], text=str(e))
                    del_link = False
    if del_link:
        msg_.delete()
    if del_link or message.from_user.id == 1503856346:
        message.delete()


@bot.on_message(filters.command(commands="restart", prefixes=trigger) & filters.user([user_]))
async def rest(bot, message):
    import sys
    os.execl(sys.executable, sys.executable, "instabot.py")
    sys.exit()


if __name__ == "__main__":
    boot()
