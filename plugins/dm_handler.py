from pyrogram import Client , filters
from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton
from helper import *
from var import *
from natsort import natsorted
import asyncio

CACHE = {}

@Client.on_message(filters.private & is_auth)
async def batch_hndlr(app , message):
    if not (CACHE.get(message.from_user.id , {}).get('start',False) and (message.video or message.document) ):
        message.continue_propagation()
    caption = message.caption or (message.video or message.document).file_name
    CACHE[message.from_user.id][caption] = message
    await replyMessage(message , '<b>Added In Batch , Send /done After Sending All Files .</b>')

@Client.on_message(filters.text & filters.private & is_auth)
async def text_handle(app , message):
    txt = message.text
    chnnl_id = str(CHANNEL_ID)[4:]
    if not txt.startswith(f'https://t.me/c/{chnnl_id}/'): message.continue_propagation()
    if len(txt.split()) == 1: message_id , end = txt.split('/')[-1] , False
    else: message_id , end = [int(x.split('/')[-1]) for x in txt.split('\n')]
    link = await gen_link(app.username , message_id , end)
    text = text = f'''<b>🔘 Here Is The Link For Your Telegram File(s) 📁

📱 TG URL :- {link}</b>'''
    reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('TG URL' , url = link)
            ]
    ])
    await replyMessage(message , text , reply_markup)

@Client.on_message(filters.private & is_auth)
async def other_handles(app , message):
    if message.text and message.text.startswith('/'): message.continue_propagation()
    post_msg = await copyMessage(message , CHANNEL_ID)
    link = await gen_link(app.username , post_msg.id)
    text = text = f'''<b>🔘 Here Is The Link For Your Telegram File(s) 📁

📱 TG URL :- {link}</b>'''
    reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('TG URL' , url = link)
            ]
    ])
    await replyMessage(message , text , reply_markup)
    if CHANNEL_BUTTON:
        await editReplyMarkup(post_msg , reply_markup)

@Client.on_message(filters.command('batchx') & filters.private & is_auth)
async def batchx(app , message):
    async def _ask(text):
        await replyMessage(message , text)
        msg = await app.listen(chat_id = message.chat.id)
        msg_id = await get_message_id(app, msg)
        if msg_id: return msg_id
        else: 
            await replyMessage(message , "<b>❌ Error , this Post is not from my DB Channel</b>")
            return await _ask(text)
    f_msg_id = await _ask('<b>Forward First Message From DB Channel Or Send Post Link !</b>')
    s_msg_id = await _ask('<b>Forward Last Message From DB Channel Or Send Post Link !</b>')
    link = await gen_link(app.username , f_msg_id , s_msg_id)
    text = text = f'''<b>🔘 Here Is The Link For Your Telegram File(s) 📁

📱 TG URL :- {link}</b>'''
    reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('TG URL' , url = link)
            ]
    ])
    await replyMessage(message , text , reply_markup)

@Client.on_message(filters.private & is_auth & filters.command('batch'))
async def batch(client, message):
    if not message.from_user.id in CACHE: CACHE[message.from_user.id] = {}
    CACHE[message.from_user.id]['start'] = True
    await replyMessage(message , '<b>Start Sending Files ...</b>')

@Client.on_message(filters.private & is_auth & filters.command('done'))
async def dn(client, message):
    if len(CACHE.get(message.from_user.id,{})) < 3 : return await replyMessage(message , '<b>Please Add More Than One Files In Batch ...</b>')
    captions = [x for x in CACHE[message.from_user.id] if x !='start']
    captions = natsorted(captions)
    prog = await replyMessage(message , f'<b>Processing Files - 0/{len(captions)}</b>')
    ctr = 0
    msg_list = []
    for i in captions:
        msg = CACHE[message.from_user.id][i]
        dn = await copyMessage(msg , CHANNEL_ID)
        msg_list.append(dn)
        ctr += 1
        if ctr % 5 == 0: await editMessage( prog , f'<b>Processing Files - {ctr}/{len(captions)}</b>')
        await asyncio.sleep(2)
    f_msg_id = msg_list[0].id
    s_msg_id = msg_list[-1].id
    link = await gen_link(client.username , f_msg_id , s_msg_id)
    text = f'''<b>🔘 Here Is The Link For Your Telegram File(s) 📁

📱 TG URL :- {link}</b>'''
    reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('TG URL' , url = link)
            ]
    ])
    await replyMessage(message , text , reply_markup)
    CACHE[message.from_user.id].clear()
    await prog.delete()

@Client.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def channel_btn(app , message):
    if not CHANNEL_BUTTON: return
    link = await gen_link(app.username , message.id)
    reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('TG URL' , url = link)
            ]
    ])
    await editReplyMarkup(message , reply_markup)
