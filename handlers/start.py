from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from helpers import is_owner, is_authorized
from keyboards import main_menu_keyboard

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        
        try:
            await db.add_user(user_id)
        except:
            pass
        
        owner = await is_owner(user_id)
        
        welcome_text = "👋 Welcome to Account Manager Bot!\n\n"
        welcome_text += "🤖 I can help you manage multiple Telegram accounts and join channels/groups automatically.\n\n"
        
        if owner:
            welcome_text += "👑 You are the Owner of this bot.\n\n"
        elif await is_authorized(user_id):
            welcome_text += "⭐ You are a Sudoer.\n\n"
        else:
            welcome_text += "👤 You are a regular user.\n\n"
        
        welcome_text += "Use the menu below to navigate through bot features."
        
        keyboard = main_menu_keyboard(owner)
        
        await message.reply_text(
            welcome_text,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Start handler error: {e}")
        try:
            keyboard = main_menu_keyboard(False)
            await message.reply_text(
                "✅ Bot is running!\n\nUse the buttons below to navigate.",
                reply_markup=keyboard
            )
        except:
            await message.reply_text("✅ Bot is running!")
