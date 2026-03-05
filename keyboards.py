from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard(is_owner=False):
    buttons = [
        [KeyboardButton("➕ Add Account"), KeyboardButton("📋 My Accounts")],
        [KeyboardButton("🔗 Join Channels"), KeyboardButton("📢 DB Channels")],
    ]
    
    if is_owner:
        buttons.append([KeyboardButton("👥 Manage Sudoers"), KeyboardButton("📊 Statistics")])
        buttons.append([KeyboardButton("⚙️ Settings"), KeyboardButton("📣 Broadcast")])
    
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def add_account_keyboard():
    keyboard = [
        [InlineKeyboardButton("Pyrogram Session", callback_data="add_pyrogram")],
        [InlineKeyboardButton("Telethon Session", callback_data="add_telethon")],
        [InlineKeyboardButton("Direct Login", callback_data="add_direct")],
        [InlineKeyboardButton("« Back", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def account_list_keyboard(accounts):
    keyboard = []
    for idx, account in enumerate(accounts):
        phone = account.get("phone", "Unknown")
        keyboard.append([InlineKeyboardButton(f"📱 {phone}", callback_data=f"account_{idx}")])
    
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def account_detail_keyboard(account_idx):
    keyboard = [
        [InlineKeyboardButton("🗑 Delete Account", callback_data=f"delete_account_{account_idx}")],
        [InlineKeyboardButton("« Back to Accounts", callback_data="show_accounts")]
    ]
    return InlineKeyboardMarkup(keyboard)

def join_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Join All Links", callback_data="join_all")],
        [InlineKeyboardButton("Join Specific Range", callback_data="join_specific")],
        [InlineKeyboardButton("« Back", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def db_channel_keyboard(channels):
    keyboard = []
    for idx, channel in enumerate(channels):
        name = channel.get("name", "Unnamed")
        keyboard.append([InlineKeyboardButton(f"📢 {name}", callback_data=f"db_channel_{idx}")])
    
    keyboard.append([InlineKeyboardButton("➕ Add DB Channel", callback_data="add_db_channel")])
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def db_channel_detail_keyboard(channel_idx):
    keyboard = [
        [InlineKeyboardButton("🚀 Use for Joining", callback_data=f"use_db_channel_{channel_idx}")],
        [InlineKeyboardButton("🗑 Delete Channel", callback_data=f"delete_db_channel_{channel_idx}")],
        [InlineKeyboardButton("« Back to Channels", callback_data="show_db_channels")]
    ]
    return InlineKeyboardMarkup(keyboard)

def join_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("Groups Only", callback_data="join_type_groups")],
        [InlineKeyboardButton("Channels Only", callback_data="join_type_channels")],
        [InlineKeyboardButton("Both", callback_data="join_type_both")],
        [InlineKeyboardButton("« Cancel", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def sudoer_keyboard(sudoers):
    keyboard = []
    for sudoer_id in sudoers:
        keyboard.append([InlineKeyboardButton(f"👤 {sudoer_id}", callback_data=f"sudoer_{sudoer_id}")])
    
    keyboard.append([InlineKeyboardButton("➕ Add Sudoer", callback_data="add_sudoer")])
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def sudoer_detail_keyboard(sudoer_id):
    keyboard = [
        [InlineKeyboardButton("🗑 Remove Sudoer", callback_data=f"remove_sudoer_{sudoer_id}")],
        [InlineKeyboardButton("« Back to Sudoers", callback_data="show_sudoers")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔓 Public Add Accounts", callback_data="toggle_public_add")],
        [InlineKeyboardButton("« Back", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_keyboard(action):
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)
