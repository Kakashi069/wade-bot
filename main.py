from bot import Bot
from uvloop import install
from pyrogram import idle

install()

async def start():
    await Bot.start()

Bot.loop.run_until_complete(start())
Bot.loop.run_forever()
idle()
