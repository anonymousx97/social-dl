import os

from dotenv import load_dotenv

load_dotenv("config.env")

# isort: skip
from .config import Config  # noqa
from app.core.message import Message  # noqa
from .core.client import BOT  # noqa

if "com.termux" not in os.environ.get("PATH", ""):
    import uvloop  # isort:skip

    uvloop.install()

bot = BOT()
