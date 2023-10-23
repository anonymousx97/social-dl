if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()

    from app import bot

    bot.run(bot.boot())
