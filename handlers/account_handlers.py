from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database import db
from helpers import can_add_accounts, format_account_info
from keyboards import add_account_keyboard, account_list_keyboard, account_detail_keyboard
from account_manager import account_manager

user_states = {}

@Client.on_message(filters.regex("^➕ Add Account$") & filters.private)
async def add_account_menu(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await can_add_accounts(user_id):
        await message.reply_text("❌ You don't have permission to add accounts.")
        return
    
    await message.reply_text(
        "📱 Choose a method to add your account:",
        reply_markup=add_account_keyboard()
    )

@Client.on_callback_query(filters.regex("^add_pyrogram$"))
async def add_pyrogram_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    user_states[user_id] = {"action": "add_pyrogram"}
    
    await callback.message.edit_text(
        "📝 Please send your Pyrogram session string:\n\n"
        "You can generate it using @StringSessionBot"
    )

@Client.on_callback_query(filters.regex("^add_telethon$"))
async def add_telethon_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    user_states[user_id] = {"action": "add_telethon"}
    
    await callback.message.edit_text(
        "📝 Please send your Telethon session string:\n\n"
        "You can generate it using @StringSessionBot"
    )

@Client.on_callback_query(filters.regex("^add_direct$"))
async def add_direct_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    user_states[user_id] = {"action": "add_direct_phone"}
    
    await callback.message.edit_text(
        "📞 Please send your phone number with country code:\n\n"
        "Example: +919876543210"
    )

@Client.on_message(filters.text & filters.private, group=1)
async def handle_text_input(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_states:
        return
    
    if message.text.startswith('/'):
        return
    
    if message.text in ["➕ Add Account", "📋 My Accounts", "🔗 Join Channels", "📢 DB Channels", 
                        "👥 Manage Sudoers", "📊 Statistics", "⚙️ Settings", "📣 Broadcast"]:
        return
    
    state = user_states[user_id]
    action = state.get("action")
    
    if action == "add_pyrogram":
        session_string = message.text.strip()
        msg = await message.reply_text("⏳ Adding Pyrogram session...")
        
        success, result = await account_manager.add_pyrogram_session(session_string, user_id)
        
        if success:
            await msg.edit_text(f"✅ {result}")
        else:
            await msg.edit_text(f"❌ {result}")
        
        del user_states[user_id]
    
    elif action == "add_telethon":
        session_string = message.text.strip()
        msg = await message.reply_text("⏳ Adding Telethon session...")
        
        success, result = await account_manager.add_telethon_session(session_string, user_id)
        
        if success:
            await msg.edit_text(f"✅ {result}")
        else:
            await msg.edit_text(f"❌ {result}")
        
        del user_states[user_id]
    
    elif action == "add_direct_phone":
        phone = message.text.strip()
        user_states[user_id]["phone"] = phone
        user_states[user_id]["action"] = "add_direct_code"
        
        try:
            from config import Config
            from pyrogram import Client as PyroClient
            
            temp_client = PyroClient(
                f"temp_{user_id}",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH
            )
            
            await temp_client.connect()
            sent_code = await temp_client.send_code(phone)
            user_states[user_id]["phone_code_hash"] = sent_code.phone_code_hash
            user_states[user_id]["temp_client"] = temp_client
            
            await message.reply_text(
                f"📨 OTP sent to {phone}\n\n"
                "Please send the verification code:"
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")
            del user_states[user_id]
    
    elif action == "add_direct_code":
        code = message.text.strip()
        phone = state.get("phone")
        phone_code_hash = state.get("phone_code_hash")
        temp_client = state.get("temp_client")
        
        try:
            await temp_client.sign_in(phone, phone_code_hash, code)
            me = await temp_client.get_me()
            session_string = await temp_client.export_session_string()
            
            account_data = {
                "type": "pyrogram",
                "session_string": session_string,
                "phone": me.phone_number,
                "user_id": me.id,
                "session_name": f"direct_{user_id}",
                "added_by": user_id
            }
            
            await db.add_account(account_data)
            await temp_client.stop()
            
            await message.reply_text(f"✅ Account {me.phone_number} added successfully!")
            del user_states[user_id]
            
        except Exception as e:
            if "Two-steps verification" in str(e) or "PASSWORD_HASH_INVALID" in str(e):
                user_states[user_id]["action"] = "add_direct_2fa"
                user_states[user_id]["code"] = code
                await message.reply_text(
                    "🔐 Two-step verification is enabled.\n\n"
                    "Please send your 2FA password:"
                )
            else:
                await message.reply_text(f"❌ Error: {str(e)}")
                if temp_client:
                    await temp_client.stop()
                del user_states[user_id]
    
    elif action == "add_direct_2fa":
        password = message.text.strip()
        phone = state.get("phone")
        phone_code_hash = state.get("phone_code_hash")
        code = state.get("code")
        temp_client = state.get("temp_client")
        
        try:
            await temp_client.check_password(password)
            me = await temp_client.get_me()
            session_string = await temp_client.export_session_string()
            
            account_data = {
                "type": "pyrogram",
                "session_string": session_string,
                "phone": me.phone_number,
                "user_id": me.id,
                "session_name": f"direct_{user_id}",
                "added_by": user_id
            }
            
            await db.add_account(account_data)
            await temp_client.stop()
            
            await message.reply_text(f"✅ Account {me.phone_number} added successfully!")
            del user_states[user_id]
            
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")
            if temp_client:
                await temp_client.stop()
            del user_states[user_id]

@Client.on_message(filters.regex("^📋 My Accounts$") & filters.private)
async def show_accounts_menu(client: Client, message: Message):
    accounts = await db.get_all_accounts()
    
    if not accounts:
        await message.reply_text("📭 You don't have any accounts added yet.")
        return
    
    await message.reply_text(
        f"📋 Total Accounts: {len(accounts)}\n\n"
        "Select an account to view details:",
        reply_markup=account_list_keyboard(accounts)
    )

@Client.on_callback_query(filters.regex("^show_accounts$"))
async def show_accounts_callback(client: Client, callback: CallbackQuery):
    accounts = await db.get_all_accounts()
    
    if not accounts:
        await callback.message.edit_text("📭 You don't have any accounts added yet.")
        return
    
    await callback.message.edit_text(
        f"📋 Total Accounts: {len(accounts)}\n\n"
        "Select an account to view details:",
        reply_markup=account_list_keyboard(accounts)
    )

@Client.on_callback_query(filters.regex("^account_"))
async def account_detail_callback(client: Client, callback: CallbackQuery):
    account_idx = int(callback.data.split("_")[1])
    accounts = await db.get_all_accounts()
    
    if account_idx >= len(accounts):
        await callback.answer("❌ Account not found!", show_alert=True)
        return
    
    account = accounts[account_idx]
    info = format_account_info(account)
    
    await callback.message.edit_text(
        f"📱 Account Details:\n\n{info}",
        reply_markup=account_detail_keyboard(account_idx)
    )

@Client.on_callback_query(filters.regex("^delete_account_"))
async def delete_account_callback(client: Client, callback: CallbackQuery):
    account_idx = int(callback.data.split("_")[2])
    accounts = await db.get_all_accounts()
    
    if account_idx >= len(accounts):
        await callback.answer("❌ Account not found!", show_alert=True)
        return
    
    account = accounts[account_idx]
    await db.delete_account(account["_id"])
    
    await callback.answer("✅ Account deleted successfully!", show_alert=True)
    await show_accounts_callback(client, callback)
