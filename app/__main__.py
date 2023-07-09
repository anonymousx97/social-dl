if __name__ == "__main__":
    import tracemalloc

    from app import bot
    import app.social_dl

    tracemalloc.start()
    bot.run(bot.boot())
