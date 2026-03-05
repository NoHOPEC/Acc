from config import Config
from database import db

async def is_owner(user_id):
    return user_id == Config.OWNER_ID

async def is_authorized(user_id):
    if await is_owner(user_id):
        return True
    return await db.is_sudoer(user_id)

async def can_add_accounts(user_id):
    if await is_authorized(user_id):
        return True
    
    public_add = await db.get_setting("public_add_enabled")
    return public_add == True

def extract_links(text):
    import re
    url_pattern = r'https?://(?:t\.me|telegram\.me|telegram\.dog)/[^\s]+'
    return re.findall(url_pattern, text)

def format_account_info(account):
    account_type = account.get("type", "Unknown")
    phone = account.get("phone", "N/A")
    session_name = account.get("session_name", "N/A")
    
    return f"Type: {account_type}\nPhone: {phone}\nSession: {session_name}"

def parse_join_range(text):
    try:
        if "-" in text:
            parts = text.split("-")
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            return start, end
        else:
            msg_id = int(text.strip())
            return msg_id, msg_id
    except:
        return None, None
