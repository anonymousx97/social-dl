import os
from logging import INFO, WARNING, StreamHandler, basicConfig, getLogger, handlers

os.makedirs("logs", exist_ok=True)

LOGGER = getLogger("Social-DL")

basicConfig(
    level=INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    handlers={
        handlers.RotatingFileHandler(
            filename="logs/app_logs.txt",
            mode="a",
            maxBytes=5 * 1024 * 1024,
            backupCount=2,
            encoding=None,
            delay=0,
        ),
        StreamHandler(),
    },
)

getLogger("pyrogram").setLevel(WARNING)
getLogger("httpx").setLevel(WARNING)
