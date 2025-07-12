from pyrogram import Client , filters
from var import *
from db import *

@Client.on_chat_join_request(filters.chat(REQUEST_FSUB))
async def request_fsub(app , message):
    if not TOGGLE: return
    await add_req(message.from_user.id)
    LOGGER(__name__).info(f"Synced {message.from_user.id} In Requests !")
