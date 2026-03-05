# Telegram Account Manager Bot

A professional Telegram bot for managing multiple Telegram accounts and automating channel/group joining.

## Features

- **Multiple Account Management**: Add accounts via Pyrogram session, Telethon session, or direct login
- **Automated Joining**: Join multiple channels/groups from DB channels
- **Owner & Sudoer System**: Role-based access control
- **MongoDB Integration**: Persistent data storage
- **Broadcast System**: Send messages to all users
- **Flexible Join Options**: Join all links or specific ranges
- **FloodWait Protection**: Smart delay system to avoid rate limits

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env` file

4. Run the bot:
```bash
python bot.py
```

## Configuration

Edit the `.env` file with your credentials:

- `BOT_TOKEN`: Your bot token from @BotFather
- `OWNER_ID`: Your Telegram user ID
- `MONGO_URI`: MongoDB connection string

## Usage

### For Owner

- Add/Remove Sudoers
- Manage all accounts
- Configure DB channels
- Broadcast messages
- View statistics
- Toggle public account adding

### For Sudoers

- Add accounts
- Manage DB channels
- Join channels/groups

### For Users

- Add accounts (if enabled by owner)
- View their accounts

## Project Structure

```
telegram-bot-project/
├── bot.py                      # Main bot file
├── config.py                   # Configuration
├── database.py                 # Database operations
├── helpers.py                  # Utility functions
├── keyboards.py                # Keyboard layouts
├── account_manager.py          # Account management
├── join_manager.py             # Joining logic
├── handlers/
│   ├── start.py               # Start command
│   ├── account_handlers.py    # Account operations
│   ├── join_handlers.py       # Join operations
│   ├── admin_handlers.py      # Admin features
│   └── callback_handlers.py   # Callback queries
├── requirements.txt            # Dependencies
└── .env                        # Environment variables
```

## License

This project is for educational purposes only.
