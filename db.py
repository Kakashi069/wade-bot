from pymongo import MongoClient
from var import *

client=MongoClient(DB_URL)
db=client[DB_NAME]
col=db['users']

users_list = []
full = col.find()
for doc in full:
        users_list.append(doc['_id'])

async def add_user(ids):
        if ids not in users_list:
                try: col.insert_one({'_id' : ids})
                except: pass
                users_list.append(ids)

async def del_user(ids):
        if ids in users_list:
                try: col.delete_one({'_id':ids})
                except: pass
                users_list.remove(ids)

# TOKEN SYSTEM
tcol = db['token']

cf = tcol.find_one({'_id':'token'})
if not cf:
        cf = {'_id':'token'}
        tcol.insert_one(cf)

async def sync():
        tcol.replace_one({'_id':'token'},cf)

# PREMIUM_USERS

prem = db['premium']

prem_dict = prem.find_one({'_id':'premium'})
if not prem_dict:
        prem_dict = {'_id':'premium'}
        prem.insert_one(prem_dict)

if 'PREMIUM' not in prem_dict: prem_dict['PREMIUM'] = {}

for key , value in prem_dict['PREMIUM'].items():
        value.update({'END' : value['END'].astimezone(TIME_ZONE)})

async def prem_sync():
        prem.replace_one({'_id':'premium'},prem_dict)

# REQUESTS USERS

req_col = db['req']

async def add_req(user_id):
        req_col.replace_one({'_id' : user_id},{'_id' : user_id},  upsert = True)

async def check_req(user_id):
        req_ = req_col.find_one({'_id' : user_id})
        return bool(req_)

## SETTINGS COL

set_col = db['settings']

rec_ = set_col.find_one({'_id' : 'settings'})

if not rec_:
        rec_ = {'_id' : 'settings'}
        set_col.insert_one(rec_)

if 'START_PIC' not in rec_: rec_['START_PIC'] = None
if 'START_TEXT' not in rec_: rec_['START_TEXT'] = None

if 'FSUB_PIC' not in rec_: rec_['FSUB_PIC'] = None
if 'FSUB_TEXT' not in rec_: rec_['FSUB_TEXT'] = None

if 'TOKEN_PIC' not in rec_: rec_['TOKEN_PIC'] = None
if 'TOKEN_TEXT' not in rec_: rec_['TOKEN_TEXT'] = None

async def sync_settings():
        set_col.replace_one({'_id' : 'settings'},rec_)