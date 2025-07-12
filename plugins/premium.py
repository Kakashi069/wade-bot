from pyrogram import Client , filters
from bot import Bot
from var import *
from helper import *
from db import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from .fsub_timeout import scheduler
from apscheduler.triggers.date import DateTrigger

id_to_task = {}

async def restart_jobs():
    if not (SHORTENER_PREMIUM and SHORTENER):
        return
    copy_data = {k : v for k , v in prem_dict['PREMIUM'].items()}
    now = datetime.now(TIME_ZONE)
    for k , v in copy_data.items():
        if v['END'] < now:
            schedule_time = now + relativedelta(seconds = 10)
        else:
            schedule_time = v['END']
        end_task = scheduler.add_job(
            premium_over , 
            DateTrigger(
                    run_date = schedule_time,
                    timezone = TIME_ZONE
                ),
            args = [int(k)]
        )
        id_to_task[int(k)] = end_task.id

Bot.loop.create_task(restart_jobs())

async def premium_over(user_id):
    del prem_dict['PREMIUM'][str(user_id)]
    await prem_sync()
    try:
        await Bot.send_message(user_id , f'''**Your Premium Subscription Has Expired Today , Please Pay Again To Admin Continue**''')
    except:
        pass
    LOGGER(__name__).info(f'Premium Over For {user_id}')

async def calc_end(now: datetime, expiry: str):
    try:
        num = int(expiry[:-1])
        unit = expiry[-1]
        if unit == 'h':
            delta = relativedelta(hours=num)
        elif unit == 'd':
            delta = relativedelta(days=num)
        elif unit == 'w':
            delta = relativedelta(weeks=num)
        elif unit == 'm':
            delta = relativedelta(months=num)
        elif unit == 'y':
            delta = relativedelta(years=num)
        elif unit == 's':
            delta = relativedelta(seconds=num)
        else:
            return None 
        return now + delta

    except (ValueError, TypeError):
        return None 
    
@Client.on_message(filters.command("addpremium") & filters.user(OWNER))
async def addpremium(app , message):
    if not (SHORTENER_PREMIUM and SHORTENER):
        return await replyMessage(message , '''`PREMIUM MODE IS OFF , TURN IT ON FIRST`''')
    try:
        user_id , expiry = message.text.split()[1:]
        user_id = int(user_id)
        user_chat = await app.get_chat(user_id)
    except:
        return await replyMessage(message , '''`Make Sure To Provide In This Format` : `/addpremium user_id expiry`

`Supported Expiry Format - h (hours) , d (days) , w (weeks) , m (months) , y (years)

Also Make Sure User Has Started The Bot !!!`''')
    now = datetime.now(TIME_ZONE)
    end = await calc_end(now , expiry)
    if not end:
        return await replyMessage(message, "`Provide Correct Expiry ! Supported Expiry Format - h (hours) , d (days) , w (weeks) , m (months) , y (years)`")
    if str(user_id) in prem_dict['PREMIUM']:
        return await replyMessage(message, f"`User Already Premium`")
    if str(user_id) not in prem_dict['PREMIUM']: prem_dict['PREMIUM'][str(user_id)] = {}
    prem_dict['PREMIUM'][str(user_id)]['NAME'] = (user_chat.first_name + " " + (user_chat.last_name or "") ).strip()
    prem_dict['PREMIUM'][str(user_id)]['END'] = end
    await replyMessage(message , f"`{prem_dict['PREMIUM'][str(user_id)]['NAME']} Added , Will Be Removed On {await readable_datetime(prem_dict['PREMIUM'][str(user_id)]['END'])}`")
    end_task = scheduler.add_job(
        premium_over , 
        DateTrigger(
                run_date = end,
                timezone = TIME_ZONE
            ),
        args = [user_id]
    )
    id_to_task[user_id] = end_task.id
    try:
        await app.send_message(user_id , f'''**You Have Been Added To Premium List , Now You Wont See Any Ads

Your Premium End Date Is : {await readable_datetime(end)}**''')
    except: pass
    await prem_sync()

async def kill_task( user_id ):
    if user_id in id_to_task:
        scheduler.remove_job(id_to_task[user_id])
        del id_to_task[user_id]

@Client.on_message(filters.command("removepremium") & filters.user(OWNER))
async def removepremium(app , message):
    if not (SHORTENER_PREMIUM and SHORTENER):
        return await replyMessage(message , '''`PREMIUM MODE IS OFF , TURN IT ON FIRST`''')
    try:
        user_id = int(message.text.split(maxsplit=1)[1])
    except:
        return await replyMessage(message , '''`Make Sure To Provide In This Format` : `/removepremium user_id`''')
    if str(user_id) not in prem_dict['PREMIUM']:
        return await replyMessage(message, "`User Is Not A Premium User`")
    name = prem_dict['PREMIUM'][str(user_id)]['NAME']
    del prem_dict['PREMIUM'][str(user_id)]
    await replyMessage(message , f"`{name} Removed !`")
    await kill_task(user_id)
    await prem_sync()

@Client.on_message(filters.command("listpremium") & filters.user(OWNER))
async def listpremium(app , message):
    if not (SHORTENER_PREMIUM and SHORTENER):
        return await replyMessage(message , '''`PREMIUM MODE IS OFF , TURN IT ON FIRST`''')
    if not prem_dict['PREMIUM']:
        return await replyMessage(message, "`No Premium Users Found`")
    string = "List Of Premium Users - \n\n"
    count = 1
    for i , j in prem_dict['PREMIUM'].items():
        string += f"{count}. {j['NAME']} [{i}] - END ON {await readable_datetime(j['END'])}\n"
    if len(string.strip()) < 4096:
        return await replyMessage(message, f"`{string.strip()}`")
    with open('premium.txt' , 'w' , encoding = 'utf-8') as f:
        f.write(string.strip())
    await message.reply_document('premium.txt' , caption = "`Premium Users List`" , quote  = True)
    os.remove('premium.txt')
