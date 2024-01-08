from app import LOGGER, bot

if __name__ == "__main__":
    bot.run(bot.boot())
else:
    LOGGER.error("Wrong Start Command.\nUse 'python -m app'")
