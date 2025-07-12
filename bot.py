from aiohttp import web
from plugins import web_server
from pyrogram import Client
import sys
from datetime import datetime
from var import *
import os

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={
                "root": "plugins"
            },
            workers=5,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):

        # INITIALIZE
        await super().start()
        self.username = (await self.get_me()).username
        self.uptime = datetime.now()
        try:
            self.db_channel = await self.get_chat(CHANNEL_ID)
            test = await self.send_message(chat_id = CHANNEL_ID, text = ".")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(f"Check DB Channel !")
            self.LOGGER(__name__).info("\nBot Stopped !")
            sys.exit()
        self.LOGGER(__name__).info(f"Bot Running..!")
        
        async def generate_invite_link(ids):
            try:
                link = (await self.get_chat(ids)).invite_link
                if not link:
                    await self.export_chat_invite_link(ids)
                    link = (await self.get_chat(ids)).invite_link
                return link
            except:
                self.LOGGER(__name__).warning(f"Check Force Sub Channel - {ids} !")
                self.LOGGER(__name__).info("\nBot Stopped !")
                sys.exit()

        # NORMAL FSUB
        self.FSUB = {}
        for index , ids in enumerate(FSUB):
            if not FSUB_LINKS: self.FSUB[ids] = await generate_invite_link(ids)
            else: self.FSUB[ids] = FSUB_LINKS[index]

        
        if os.path.exists('.restartmsg'):
            with open(".restartmsg") as f:
                chat_id, msg_id = map(int, f)
                try:
                    await self.edit_message_text(chat_id=chat_id, message_id=msg_id, text="`Restarted !`")
                    os.remove('.restartmsg')
                except Exception as e:
                    pass
        # WEB BIND
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

Bot = Bot()