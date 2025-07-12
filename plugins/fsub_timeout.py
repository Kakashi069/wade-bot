from var import *
from bot import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

scheduler = AsyncIOScheduler()

scheduler.start()

async def perform():
    for channel , link in Bot.FSUB.items():
        await Bot.revoke_chat_invite_link(channel, link)
        link = await Bot.create_chat_invite_link(channel)
        link = link.invite_link
        Bot.FSUB[channel] = link
    LOGGER(__name__).info('Generated New Links')

if FSUB_TIMEOUT and FSUB:
    scheduler.add_job(
        perform, 
        'date',
        run_date=datetime.now() + timedelta(seconds=5)
    )
    scheduler.add_job(
        perform,
        'interval',
        seconds = FSUB_TIMEOUT
)