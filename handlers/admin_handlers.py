from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database import db
from helpers import is_owner
from keyboards import sudoer_keyboard, sudoer_detail_keyboard, settings_keyboard

admin_states = {}

@Client.on_message(filters.regex("^👥 Manage Sudoers$") & filters.private)
async def manage_sudoers_menu(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await is_owner(user_id):
        await message.reply_text("❌ This feature is only for the owner.")
        return
    
    sudoers = await db.get_sudoers()
    
    await message.reply_text(
        f"👥 Sudoers: {len(sudoers)}\n\n"
        "Select a sudoer to manage:",
        reply_markup=sudoer_keyboard(sudoers)
    )

@Client.on_callback_query(filters.regex("^show_sudoers$"))
async def show_sudoers_callback(client: Client, callback: CallbackQuery):
    sudoers = await db.get_sudoers()
    
    await callback.message.edit_text(
        f"👥 Sudoers: {len(sudoers)}\n\n"
        "Select a sudoer to manage:",
        reply_markup=sudoer_keyboard(sudoers)
    )

@Client.on_callback_query(filters.regex("^add_sudoer$"))
async def add_sudoer_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    admin_states[user_id] = {"action": "add_sudoer"}
    
    await callback.message.edit_text(
        "📝 Send the user ID to add as sudoer:\n\n"
        "Example: 123456789"
    )

@Client.on_callback_query(filters.regex("^sudoer_"))
async def sudoer_detail_callback(client: Client, callback: CallbackQuery):
    sudoer_id = int(callback.data.split("_")[1])
    
    await callback.message.edit_text(
        f"👤 Sudoer ID: {sudoer_id}\n\n"
        "Manage this sudoer:",
        reply_markup=sudoer_detail_keyboard(sudoer_id)
    )

@Client.on_callback_query(filters.regex("^remove_sudoer_"))
async def remove_sudoer_callback(client: Client, callback: CallbackQuery):
    sudoer_id = int(callback.data.split("_")[2])
    
    await db.remove_sudoer(sudoer_id)
    await callback.answer("✅ Sudoer removed!", show_alert=True)
    
    await show_sudoers_callback(client, callback)

@Client.on_message(filters.regex("^📊 Statistics$") & filters.private)
async def statistics_menu(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await is_owner(user_id):
        await message.reply_text("❌ This feature is only for the owner.")
        return
    
    total_users = len(await db.get_all_users())
    total_accounts = len(await db.get_all_accounts())
    total_sudoers = len(await db.get_sudoers())
    total_channels = len(await db.get_all_db_channels())
    
    stats_text = f"""
📊 Bot Statistics

👥 Total Users: {total_users}
📱 Total Accounts: {total_accounts}
⭐ Total Sudoers: {total_sudoers}
📢 DB Channels: {total_channels}
"""
    
    await message.reply_text(stats_text)

@Client.on_message(filters.regex("^⚙️ Settings$") & filters.private)
async def settings_menu(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await is_owner(user_id):
        await message.reply_text("❌ This feature is only for the owner.")
        return
    
    public_add = await db.get_setting("public_add_enabled")
    status = "✅ Enabled" if public_add else "❌ Disabled"
    
    await message.reply_text(
        f"⚙️ Bot Settings\n\n"
        f"Public Add Accounts: {status}\n\n"
        "Use the button below to toggle:",
        reply_markup=settings_keyboard()
    )

@Client.on_callback_query(filters.regex("^toggle_public_add$"))
async def toggle_public_add_callback(client: Client, callback: CallbackQuery):
    current = await db.get_setting("public_add_enabled")
    new_value = not current if current is not None else True
    
    await db.set_setting("public_add_enabled", new_value)
    
    status = "✅ Enabled" if new_value else "❌ Disabled"
    await callback.answer(f"Public Add: {status}", show_alert=True)
    
    await callback.message.edit_text(
        f"⚙️ Bot Settings\n\n"
        f"Public Add Accounts: {status}\n\n"
        "Use the button below to toggle:",
        reply_markup=settings_keyboard()
    )

@Client.on_message(filters.text & filters.private, group=2)
async def handle_admin_text_input(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in admin_states:
        return
    
    if message.text.startswith('/'):
        return
    
    if message.text in ["➕ Add Account", "📋 My Accounts", "🔗 Join Channels", "📢 DB Channels", 
                        "👥 Manage Sudoers", "📊 Statistics", "⚙️ Settings", "📣 Broadcast"]:
        return
    
    state = admin_states[user_id]
    action = state.get("action")
    
    if action == "add_sudoer":
        try:
            new_sudoer_id = int(message.text.strip())
            
            if new_sudoer_id == user_id:
                await message.reply_text("❌ You cannot add yourself as sudoer!")
                del admin_states[user_id]
                return
            
            await db.add_sudoer(new_sudoer_id)
            await message.reply_text(f"✅ User {new_sudoer_id} added as sudoer!")
            
            del admin_states[user_id]
        except ValueError:
            await message.reply_text("❌ Invalid user ID! Please send a numeric ID.")
    
    elif action == "broadcast_message":
        broadcast_text = message.text
        users = await db.get_all_users()
        
        success = 0
        failed = 0
        
        progress_msg = await message.reply_text(
            f"📢 Broadcasting to {len(users)} users...\n\n"
            f"⏳ Progress: 0/{len(users)}"
        )
        
        for idx, target_user_id in enumerate(users):
            try:
                await client.send_message(target_user_id, broadcast_text)
                success += 1
            except:
                failed += 1
            
            if (idx + 1) % 10 == 0:
                await progress_msg.edit_text(
                    f"📢 Broadcasting...\n\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"⏳ Progress: {idx + 1}/{len(users)}"
                )
        
        await progress_msg.edit_text(
            f"✅ Broadcast Completed!\n\n"
            f"✅ Success: {success}\n"
            f"❌ Failed: {failed}\n"
            f"📊 Total: {len(users)}"
        )
        
        del admin_states[user_id]

@Client.on_message(filters.regex("^📣 Broadcast$") & filters.private)
async def broadcast_menu(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await is_owner(user_id):
        await message.reply_text("❌ This feature is only for the owner.")
        return
    
    admin_states[user_id] = {"action": "broadcast_message"}
    
    await message.reply_text(
        "📣 Send the message you want to broadcast to all users:\n\n"
        "This message will be sent to all users who have started the bot."
    )
