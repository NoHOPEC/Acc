from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from keyboards import main_menu_keyboard
from helpers import is_owner

@Client.on_callback_query(filters.regex("^back_main$"))
async def back_main_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    owner = await is_owner(user_id)
    
    await callback.message.edit_text(
        "🏠 Main Menu\n\n"
        "Use the keyboard below to navigate:",
        reply_markup=main_menu_keyboard(owner)
    )
