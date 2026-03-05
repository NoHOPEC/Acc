from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database import db
from helpers import is_authorized
from keyboards import join_menu_keyboard, join_type_keyboard, db_channel_keyboard, db_channel_detail_keyboard
from join_manager import join_manager

join_states = {}

@Client.on_message(filters.regex("^🔗 Join Channels$") & filters.private)
async def join_menu(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await is_authorized(user_id):
        await message.reply_text("❌ You don't have permission to use this feature.")
        return
    
    await message.reply_text(
        "🔗 Choose joining method:",
        reply_markup=join_menu_keyboard()
    )

@Client.on_callback_query(filters.regex("^join_all$"))
async def join_all_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    
    channels = await db.get_all_db_channels()
    if not channels:
        await callback.answer("❌ No DB channels configured!", show_alert=True)
        return
    
    join_states[user_id] = {"mode": "all"}
    
    await callback.message.edit_text(
        "📢 Select a DB channel to fetch links from:",
        reply_markup=db_channel_keyboard(channels)
    )

@Client.on_callback_query(filters.regex("^join_specific$"))
async def join_specific_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    join_states[user_id] = {"mode": "specific", "action": "awaiting_range"}
    
    await callback.message.edit_text(
        "📝 Send the message ID range to join:\n\n"
        "Format:\n"
        "• Single message: 123\n"
        "• Range: 100-200\n\n"
        "Example: 50-150"
    )

@Client.on_callback_query(filters.regex("^use_db_channel_"))
async def use_db_channel_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    channel_idx = int(callback.data.split("_")[3])
    
    channels = await db.get_all_db_channels()
    if channel_idx >= len(channels):
        await callback.answer("❌ Channel not found!", show_alert=True)
        return
    
    channel = channels[channel_idx]
    join_states[user_id]["channel"] = channel
    
    await callback.message.edit_text(
        "🎯 Select join type:",
        reply_markup=join_type_keyboard()
    )

@Client.on_callback_query(filters.regex("^join_type_"))
async def join_type_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    join_type = callback.data.split("_")[2]
    
    if user_id not in join_states:
        await callback.answer("❌ Session expired!", show_alert=True)
        return
    
    state = join_states[user_id]
    channel = state.get("channel")
    mode = state.get("mode", "all")
    
    accounts = await db.get_all_accounts()
    if not accounts:
        await callback.answer("❌ No accounts added!", show_alert=True)
        return
    
    await callback.message.edit_text("⏳ Fetching links from DB channel...")
    
    start_id = state.get("start_id")
    end_id = state.get("end_id")
    
    links = await join_manager.fetch_links_from_channel(
        client,
        channel.get("username"),
        start_id,
        end_id
    )
    
    if not links:
        await callback.message.edit_text("❌ No links found in the specified range!")
        del join_states[user_id]
        return
    
    progress_msg = await callback.message.edit_text(
        f"🚀 Starting join process...\n\n"
        f"📊 Total Links: {len(links)}\n"
        f"👥 Total Accounts: {len(accounts)}\n"
        f"🎯 Join Type: {join_type.capitalize()}\n\n"
        f"⏳ Progress: 0%"
    )
    
    async def update_progress(progress, acc_num, total_acc, link_num, total_links):
        await progress_msg.edit_text(
            f"🚀 Join Process Active...\n\n"
            f"📊 Total Links: {total_links}\n"
            f"👥 Account: {acc_num}/{total_acc}\n"
            f"🔗 Link: {link_num}/{total_links}\n\n"
            f"⏳ Progress: {progress:.1f}%"
        )
    
    results = await join_manager.join_links(
        accounts,
        links,
        join_type,
        update_progress
    )
    
    await progress_msg.edit_text(
        f"✅ Join Process Completed!\n\n"
        f"✅ Success: {results['success']}\n"
        f"⚠️ Already Member: {results['already_member']}\n"
        f"❌ Failed: {results['failed']}\n\n"
        f"📊 Total Processed: {len(links) * len(accounts)}"
    )
    
    del join_states[user_id]

@Client.on_message(filters.regex("^📢 DB Channels$") & filters.private)
async def db_channels_menu(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await is_authorized(user_id):
        await message.reply_text("❌ You don't have permission to manage DB channels.")
        return
    
    channels = await db.get_all_db_channels()
    
    await message.reply_text(
        f"📢 DB Channels: {len(channels)}\n\n"
        "Select a channel to view details:",
        reply_markup=db_channel_keyboard(channels)
    )

@Client.on_callback_query(filters.regex("^show_db_channels$"))
async def show_db_channels_callback(client: Client, callback: CallbackQuery):
    channels = await db.get_all_db_channels()
    
    await callback.message.edit_text(
        f"📢 DB Channels: {len(channels)}\n\n"
        "Select a channel to view details:",
        reply_markup=db_channel_keyboard(channels)
    )

@Client.on_callback_query(filters.regex("^add_db_channel$"))
async def add_db_channel_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    join_states[user_id] = {"action": "add_db_channel"}
    
    await callback.message.edit_text(
        "📝 Send the DB channel details:\n\n"
        "Format: Channel Name | @username\n\n"
        "Example: My DB Channel | @mydbchannel"
    )

@Client.on_callback_query(filters.regex("^db_channel_"))
async def db_channel_detail_callback(client: Client, callback: CallbackQuery):
    channel_idx = int(callback.data.split("_")[2])
    channels = await db.get_all_db_channels()
    
    if channel_idx >= len(channels):
        await callback.answer("❌ Channel not found!", show_alert=True)
        return
    
    channel = channels[channel_idx]
    
    await callback.message.edit_text(
        f"📢 DB Channel Details:\n\n"
        f"Name: {channel.get('name')}\n"
        f"Username: @{channel.get('username')}",
        reply_markup=db_channel_detail_keyboard(channel_idx)
    )

@Client.on_callback_query(filters.regex("^delete_db_channel_"))
async def delete_db_channel_callback(client: Client, callback: CallbackQuery):
    channel_idx = int(callback.data.split("_")[3])
    channels = await db.get_all_db_channels()
    
    if channel_idx >= len(channels):
        await callback.answer("❌ Channel not found!", show_alert=True)
        return
    
    channel = channels[channel_idx]
    await db.delete_db_channel(channel["_id"])
    
    await callback.answer("✅ DB Channel deleted!", show_alert=True)
    await show_db_channels_callback(client, callback)

@Client.on_message(filters.text & filters.private, group=3)
async def handle_join_text_input(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in join_states:
        return
    
    if message.text.startswith('/'):
        return
    
    if message.text in ["➕ Add Account", "📋 My Accounts", "🔗 Join Channels", "📢 DB Channels", 
                        "👥 Manage Sudoers", "📊 Statistics", "⚙️ Settings", "📣 Broadcast"]:
        join_states.pop(user_id, None)
        return
    
    state = join_states[user_id]
    action = state.get("action")
    
    if action == "add_db_channel":
        try:
            text = message.text.strip()
            
            if text.startswith("https://t.me/"):
                if "/+" in text or "/joinchat/" in text:
                    invite_hash = text.split("/")[-1]
                    name = f"Private Channel {invite_hash[:8]}"
                    username = invite_hash
                else:
                    username = text.split("/")[-1].replace("@", "")
                    name = f"Channel @{username}"
            elif "|" in text:
                parts = text.split("|")
                name = parts[0].strip()
                username = parts[1].strip().replace("@", "")
            else:
                await message.reply_text(
                    "❌ Invalid format!\n\n"
                    "Send either:\n"
                    "• Channel link: https://t.me/username\n"
                    "• Private link: https://t.me/+xyz\n"
                    "• Format: Name | @username"
                )
                return
            
            channel_data = {
                "name": name,
                "username": username,
                "is_private": "/+" in text or "/joinchat/" in text
            }
            
            await db.add_db_channel(channel_data)
            await message.reply_text(f"✅ DB Channel '{name}' added successfully!")
            
            join_states.pop(user_id, None)
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")
            join_states.pop(user_id, None)
    
    elif action == "awaiting_range":
        try:
            text = message.text.strip()
            
            if "-" in text:
                parts = text.split("-")
                start_id = int(parts[0].strip())
                end_id = int(parts[1].strip())
            else:
                start_id = end_id = int(text)
            
            join_states[user_id]["start_id"] = start_id
            join_states[user_id]["end_id"] = end_id
            join_states[user_id]["action"] = "select_channel"
            
            channels = await db.get_all_db_channels()
            await message.reply_text(
                f"✅ Range set: {start_id} to {end_id}\n\n"
                "📢 Select a DB channel:",
                reply_markup=db_channel_keyboard(channels)
            )
        except Exception as e:
            await message.reply_text(
                f"❌ Invalid format! {str(e)}\n\n"
                "Use: 123 or 100-200"
            )
            join_states.pop(user_id, None)
