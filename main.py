from alicebot import Bot

bot = Bot(hot_reload=True)
# bot.load_plugins_from_dirs("plugins", "./plugins")
if __name__ == "__main__":
    print('running...')

    ### 不开代理时,可能由于crawler.py中的访问cf题目集函数卡住导致不能正常加载插件 .
    bot.run()
