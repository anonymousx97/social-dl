from dotenv import load_dotenv

load_dotenv("config.env")

from .config import Config
from .core.client import BOT


bot = BOT()
