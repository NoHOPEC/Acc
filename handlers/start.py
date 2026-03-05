from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from helpers import is_owner, is_authorized
from keyboards import main_menu_keyboard

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    await db.add_user(user_id)
    
    owner = await is_owner(user_id)
    authorized = await is_authorized(user_id)
    
    welcome_text = f"""
👋 Welcome to Account Manager Bot!

🤖 I can help you manage multiple Telegram accounts and join channels/groups automatically.

"""
    
    if owner:
        welcome_text += "👑 You are the Owner of this bot.\n\n"
    elif authorized:
        welcome_text += "⭐ You are a Sudoer.\n\n"
    else:
        welcome_text += "👤 You are a regular user.\n\n"
    
    welcome_text += "Use the menu below to navigate through bot features."
    
    await message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard(owner)
    )
