from pyrogram import Client , filters
from var import *
from helper import *
from db import *
import os , sys
import aiohttp , base64 , re
from urllib.parse import urlparse

async def update_github_file(repo_url: str, branch: str, file_name: str, new_content: str):
    parsed_url = urlparse(repo_url)
    token = re.search(r"ghp_\w+", parsed_url.netloc).group(0)
    repo_parts = parsed_url.path.strip("/").split("/")
    repo_owner, repo_name = repo_parts[0], repo_parts[1]

    file_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_name}"
    headers = {"Authorization": f"token {token}"}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(file_url, params={"ref": branch}) as response:
            if response.status != 200:
                print(f"Error fetching file: {response.status}")
                return False
            
            file_data = await response.json()
            file_sha = file_data["sha"] 
            print(f"Current file content retrieved successfully. SHA: {file_sha}")

        new_content_encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
        payload = {
            "message": f"Updating {file_name} via API",
            "content": new_content_encoded,
            "branch": branch,
            "sha": file_sha,
        }
        async with session.put(file_url, json=payload) as response:
            if response.status == 200:
                print(f"File updated successfully: {file_name}")
                return True
            else:
                print(f"Error updating file: {response.status}")
                return False


def parse_config(file_path="./config.env"):
    config_vars = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            line = line.split('#')[0].strip()
            if not line or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            
            if value.isdigit():
                value = int(value)
            elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            if key == "UPSTREAM_REPO" or key == "UPSTREAM_BRANCH" or key == "CURRENT_REPO" or key == "CURRENT_BRANCH":
                continue
            config_vars[key] = value
        file.close()
    
    return config_vars

def split_list(li):
    return [li[x:x + 2] for x in range(0, len(li), 2)]

config_vars = parse_config() # This is Use to Store Varaiable 

@Client.on_message(filters.private & filters.command('bs') & filters.user(OWNER))
async def bsettings(app , message):
    if not CURRENT_REPO or not CURRENT_BRANCH:
        return await replyMessage(message , '**Fill Up CURRENT_REPO & CURRENT_BRANCH First !**')
    
    button = []
    txt = ""

    for key, value in config_vars.items():
        txt += f"{key}: `{value}`\n"
        button.append(InlineKeyboardButton(key, callback_data=key))

    for key , value in rec_.items():
        if key == '_id': continue
        txt += f"{key}: `{value}`\n"
        button.append(InlineKeyboardButton(key, callback_data=f"dbset_{key}"))
    
    button = split_list(button)
    button.append([InlineKeyboardButton("👾 Push 👾", callback_data="b_push"), InlineKeyboardButton("💀 Close 💀", callback_data="b_close")])
    button.append([InlineKeyboardButton("👾 Refresh 👾", callback_data="ref")])
    await replyMessage(message , txt, reply_markup=InlineKeyboardMarkup(button))
    
@Client.on_callback_query(filters.user(OWNER))
async def callback_handler(_, query):
    if query.data == "b_close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            pass
    
    elif query.data == "b_push":
        def update_config_file(config_vars):
            with open("config.env", "r") as file:
                lines = file.readlines()
            
            new_lines = []
            for line in lines:
                if "=" in line:
                    key = line.split("=", 1)[0].strip()
                    if key in config_vars:
                        value = config_vars[key]
                        if isinstance(value, str) and not value.isdigit() and value not in ("True", "False"):
                            new_line = f'{key} = "{value}"\n'
                        else:
                            new_line = f"{key} = {value}\n"
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)  # Keep original line
                else:
                    new_lines.append(line)  # Keep comments/empty lines
            
            with open("config.env", "w") as file:
                file.writelines(new_lines)
        
        update_config_file(config_vars)
        with open("config.env", "r") as file:
            lines = file.read()
        status = await update_github_file(CURRENT_REPO , CURRENT_BRANCH , 'config.env' , lines)
        msg = await replyMessage(query.message , f'`Succesfully Changed, Now Restarting !`')
        
        with open(".restartmsg", "w") as f:
            f.write(f"{msg.chat.id}\n{msg.id}\n")
        
        os.execl(sys.executable, sys.executable, '-B' , "main.py")
    elif query.data == "ref":
        button = []
        txt = ""
        for key, value in config_vars.items():
            txt += f"{key}: `{value}`\n"
            button.append(InlineKeyboardButton(key, callback_data=key))
        for key , value in rec_.items():
            if key == '_id': continue
            txt += f"{key}: `{value}`\n"
            button.append(InlineKeyboardButton(key, callback_data=f"dbset_{key}"))
        button = split_list(button)
        button.append([InlineKeyboardButton("👾 Push 👾", callback_data="b_push"), InlineKeyboardButton("💀 Close 💀", callback_data="b_close")])
        button.append([InlineKeyboardButton("👾 Refresh 👾", callback_data="ref")])
        try:
            await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(button))
        except FloodWait as e:
            LOGGER(__name__).info(f"Sleeping for {e.value} Seconds")
            await asyncio.sleep(e.value * 1.5)
            await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(button))
        except MessageNotModified:
            await query.edit_message_text("....")
            try:
                await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(button))
            except FloodWait as e:
                LOGGER(__name__).info(f"Sleeping for {e.value} Seconds")
                await asyncio.sleep(e.value * 1.5)
                await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(button))
    elif query.data.startswith('dbset'):
        key = query.data.split('_' , maxsplit = 1)[1]
        if key not in rec_: await editMessage(sts, "**No Found**")
        sts = await query.message.reply_text("<code>Send The Value...</code>\nTo Cancel: `/cancel`")
        if True:
            try:
                call = await _.listen(user_id=query.from_user.id, timeout=90)
                if call.text == "/cancel":
                    return await editMessage(sts, "`Process Cancel`")
                if call.text and call.text == 'delete':
                    rec_[key] = None
                else:
                    if key.endswith('TEXT'): rec_[key] = call.text
                    else: rec_[key] = (call.document or call.video or call.photo or call.audio or call.animation).file_id
                await sync_settings()
                await call.delete()
                
                button = []
                text = ""
                for key, value in config_vars.items():
                    text += f"{key}: `{value}`\n"
                    button.append(InlineKeyboardButton(key, callback_data=key))
                
                for key , value in rec_.items():
                    if key == '_id': continue
                    text += f"{key}: `{value}`\n"
                    button.append(InlineKeyboardButton(key, callback_data=f"dbset_{key}"))
                
                button = split_list(button)
                button.append([InlineKeyboardButton("👾 Push 👾", callback_data="b_push"), InlineKeyboardButton("💀 Close 💀", callback_data="b_close")])
                button.append([InlineKeyboardButton("👾 Refresh 👾", callback_data="ref")])
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(button))
                except FloodWait as e:
                    LOGGER(__name__).info(f"Sleeping for {e.value} Seconds")
                    await asyncio.sleep(e.value * 1.5)
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(button))
                except MessageNotModified:
                    await query.edit_message_text("**you send me same thing that already set in config.py**")
                
                await sts.delete()
            except Exception as err:
                await sts.edit(err)
    
    else:
        key = query.data
        sts = await query.message.reply_text("<code>Send The Value...</code>\nTo Cancel: `/cancel`")
        if key in config_vars:
            try:
                call = await _.listen(user_id=query.from_user.id, timeout=90)
                if call.text == "/cancel":
                    return await editMessage(sts, "`Process Cancel`")
                config_vars[key] = call.text
                await call.delete()
                
                button = []
                text = ""
                for key, value in config_vars.items():
                    text += f"{key}: `{value}`\n"
                    button.append(InlineKeyboardButton(key, callback_data=key))
                
                for key , value in rec_.items():
                    if key == '_id': continue
                    text += f"{key}: `{value}`\n"
                    button.append(InlineKeyboardButton(key, callback_data=f"dbset_{key}"))
                
                button = split_list(button)
                button.append([InlineKeyboardButton("👾 Push 👾", callback_data="b_push"), InlineKeyboardButton("💀 Close 💀", callback_data="b_close")])
                button.append([InlineKeyboardButton("👾 Refresh 👾", callback_data="ref")])
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(button))
                except FloodWait as e:
                    LOGGER(__name__).info(f"Sleeping for {e.value} Seconds")
                    await asyncio.sleep(e.value * 1.5)
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(button))
                except MessageNotModified:
                    await query.edit_message_text("**you send me same thing that already set in config.py**")
                
                await sts.delete()
            except Exception as err:
                await sts.edit(err)
        else:
            await editMessage(sts, "**No Found**")
    
    try: await query.answer()
    except: pass
        
        
@Client.on_message(filters.private & filters.command('change') & filters.user(OWNER))
async def change(app , message):
    if not CURRENT_REPO or not CURRENT_BRANCH:
        return await replyMessage(message , '**Fill Up CURRENT_REPO & CURRENT_BRANCH First !**')
    try:
        key , value =[ i.strip() for i in message.text.split(maxsplit=1)[1].strip().split('=' , maxsplit=1 ) ]
    except:
        return await replyMessage(message , '**Send Correctly In Format Like `/change FSUB = "-100xx -100xx"`**')
    with open("config.env", "r") as file:
        lines = file.readlines()
    status = None
    with open("config.env", "w") as file:
        for line in lines:
            if line.split("=" , maxsplit=1)[0].strip() == key:
                file.write(f"{key} = {value}\n")
                status = True
            else:
                file.write(line)
    if not status: return await replyMessage(message , '**`No Such Variable Found !`**')
    with open("config.env", "r") as file:
        lines = file.read()
    status = await update_github_file(CURRENT_REPO , CURRENT_BRANCH , 'config.env' , lines)
    msg = await replyMessage(message , f'`Succesfully Changed {key} = {value}, Now Restarting !`')
    with open(".restartmsg", "w") as f:
        f.write(f"{msg.chat.id}\n{msg.id}\n")
    os.execl(sys.executable, sys.executable, '-B' , "main.py")
