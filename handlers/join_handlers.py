from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from database import db
from helpers import is_authorized
from keyboards import join_menu_keyboard, join_type_keyboard, db_channel_keyboard, db_channel_detail_keyboard
from join_manager import join_manager
from account_manager import account_manager

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
    join_states[user_id]["channel_username"] = channel.get("username")
    
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
    channel_username = state.get("channel_username")
    
    accounts = await db.get_all_accounts()
    if not accounts:
        await callback.answer("❌ No accounts added!", show_alert=True)
        return
    
    progress_msg = await callback.message.edit_text(
        f"⏳ Step 1/3: Joining DB channel with all accounts...\n\n"
        f"👥 Total Accounts: {len(accounts)}"
    )
    
    start_id = state.get("start_id")
    end_id = state.get("end_id")
    
    joined_accounts = []
    failed_accounts = []
    db_chat = None
    
    for idx, account in enumerate(accounts):
        phone = account.get("phone", "Unknown")
        try:
            acc_client = await account_manager.get_client(account)
            if not acc_client:
                failed_accounts.append(f"{phone} (Client creation failed)")
                continue
            
            await acc_client.start()
            
            try:
                if channel_username.startswith("https://"):
                    chat = await acc_client.join_chat(channel_username)
                    if not db_chat:
                        db_chat = chat
                else:
                    username = channel_username.replace("@", "")
                    chat = await acc_client.join_chat(username)
                    if not db_chat:
                        db_chat = chat
                joined_accounts.append(account)
            except Exception as e:
                error_str = str(e).lower()
                if "already" in error_str or "participant" in error_str:
                    if not db_chat:
                        try:
                            if channel_username.startswith("https://"):
                                db_chat = await acc_client.get_chat(channel_username)
                            else:
                                db_chat = await acc_client.get_chat(channel_username.replace("@", ""))
                        except:
                            pass
                    joined_accounts.append(account)
                else:
                    failed_accounts.append(f"{phone} ({str(e)[:50]})")
            
            try:
                await acc_client.stop()
            except:
                pass
            
            if (idx + 1) % 3 == 0 or idx == len(accounts) - 1:
                await progress_msg.edit_text(
                    f"⏳ Step 1/3: Joining DB channel...\n\n"
                    f"👥 Progress: {idx + 1}/{len(accounts)}\n"
                    f"✅ Joined: {len(joined_accounts)}\n"
                    f"❌ Failed: {len(failed_accounts)}"
                )
            
        except Exception as e:
            failed_accounts.append(f"{phone} ({str(e)[:50]})")
    
    if not joined_accounts:
        error_details = "\n".join([f"• {acc}" for acc in failed_accounts[:5]])
        await progress_msg.edit_text(
            f"❌ No accounts could join DB channel!\n\n"
            f"Failed accounts ({len(failed_accounts)}):\n{error_details}\n\n"
            f"Common issues:\n"
            f"• Session expired - Re-add account\n"
            f"• Invalid link format\n"
            f"• Account restricted"
        )
        join_states.pop(user_id, None)
        return
    
    await progress_msg.edit_text(
        f"⏳ Step 2/3: Fetching links from DB channel...\n\n"
        f"Using first account..."
    )
    
    links = []
    message_count = 0
    
    try:
        first_account = joined_accounts[0]
        fetch_client = await account_manager.get_client(first_account)
        await fetch_client.start()
        
        async for message in fetch_client.get_chat_history(channel_username):
            message_count += 1
            
            if start_id and end_id:
                if message.id < start_id or message.id > end_id:
                    continue
            elif start_id:
                if message.id != start_id:
                    continue
            
            if message.text:
                found_links = join_manager.extract_links(message.text)
                links.extend(found_links)
            
            if message.caption:
                found_links = join_manager.extract_links(message.caption)
                links.extend(found_links)
        
        await fetch_client.stop()
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Error: {str(e)}\n\nChecked: {message_count} messages")
        join_states.pop(user_id, None)
        return
    
    if not links:
        await progress_msg.edit_text(
            f"❌ No links found in DB channel!\n\n"
            f"Checked {message_count} messages\n"
            f"Range: {start_id or 'All'} to {end_id or 'All'}\n\n"
            "Make sure:\n"
            "• DB channel has messages\n"
            "• Messages contain t.me links"
        )
        join_states.pop(user_id, None)
        return
    
    unique_links = list(set(links))
    
    await progress_msg.edit_text(
        f"⏳ Step 3/3: Joining {len(unique_links)} links...\n\n"
        f"📊 Total Links: {len(unique_links)}\n"
        f"👥 Total Accounts: {len(joined_accounts)}\n"
        f"🎯 Join Type: {join_type.capitalize()}\n\n"
        f"⏳ Progress: 0%"
    )
    
    async def update_progress(progress, acc_num, total_acc, link_num, total_links):
        try:
            await progress_msg.edit_text(
                f"🚀 Step 3/3: Joining links...\n\n"
                f"📊 Total Links: {total_links}\n"
                f"👥 Account: {acc_num}/{total_acc}\n"
                f"🔗 Link: {link_num}/{total_links}\n\n"
                f"⏳ Progress: {progress:.1f}%"
            )
        except:
            pass
    
    results = await join_manager.join_links(
        joined_accounts,
        unique_links,
        join_type,
        update_progress
    )
    
    await progress_msg.edit_text(
        f"✅ All Steps Completed!\n\n"
        f"Step 1 - DB Channel Join:\n"
        f"✅ Success: {len(joined_accounts)}\n"
        f"❌ Failed: {len(failed_accounts)}\n\n"
        f"Step 2 - Links Found: {len(unique_links)}\n\n"
        f"Step 3 - Joining Results:\n"
        f"✅ Success: {results['success']}\n"
        f"⚠️ Already Member: {results['already_member']}\n"
        f"❌ Failed: {results['failed']}"
    )
    
    join_states.pop(user_id, None)

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
                    full_link = text
                    invite_hash = text.split("/")[-1]
                    name = f"Private Channel {invite_hash[:8]}"
                    username = full_link
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
