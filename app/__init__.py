import os
import tracemalloc

from dotenv import load_dotenv

load_dotenv("config.env")
tracemalloc.start()


# isort: skip
from app.config import Config  # NOQA
from app.core import LOGGER, Message  # NOQA
from app.core.client.client import BOT  # NOQA

if "com.termux" not in os.environ.get("PATH", ""):
    import uvloop  # isort:skip

    uvloop.install()

bot: BOT = BOT()
