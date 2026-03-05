# Setup Guide - Telegram Account Manager Bot

## Quick Start

### Step 1: Prerequisites

- Python 3.11 or higher
- MongoDB database (free tier available at MongoDB Atlas)
- Telegram Bot Token from @BotFather

### Step 2: Installation

1. Extract the project folder

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 3: Configuration

Your `.env` file is already configured with:
- Bot Token: 7610778997:AAHy4oa_H4dC21W1RWfwLNqeBYG5-qQec48
- Owner ID: 7574330905
- MongoDB URI: mongodb+srv://pusers:nycreation@nycreation.pd4klp1.mongodb.net/...

### Step 4: Run the Bot

```bash
python bot.py
```

## Features Overview

### 1. Account Management

**Add Account Methods:**
- **Pyrogram Session**: Paste session string from @StringSessionBot
- **Telethon Session**: Paste Telethon session string
- **Direct Login**: Login with phone number + OTP + 2FA (if enabled)

**Commands:**
- Click "➕ Add Account" to add new accounts
- Click "📋 My Accounts" to view and manage accounts
- Delete accounts from account details page

### 2. DB Channels

**Setup DB Channels:**
1. Click "📢 DB Channels"
2. Click "➕ Add DB Channel"
3. Send: `Channel Name | @username`

Example: `Main DB | @mydbchannel`

**DB Channel Structure:**
- Store group/channel invite links in your DB channel
- Links can be in any message format
- Bot will extract all t.me links automatically

### 3. Joining Channels/Groups

**Join All Links:**
1. Click "🔗 Join Channels"
2. Click "Join All Links"
3. Select DB channel
4. Select join type (Groups/Channels/Both)
5. Wait for completion

**Join Specific Range:**
1. Click "🔗 Join Channels"
2. Click "Join Specific Range"
3. Send message ID range (e.g., `100-200` or `150`)
4. Select DB channel
5. Select join type
6. Wait for completion

**Features:**
- Automatic FloodWait handling
- 3-second delay between joins
- Progress tracking
- Success/Failure statistics

### 4. Owner Features

**Manage Sudoers:**
- Add users who can manage accounts and join channels
- Remove sudoers
- View sudoer list

**Statistics:**
- View total users
- Total accounts
- Total sudoers
- Total DB channels

**Settings:**
- Toggle public account adding
- When enabled, anyone can add accounts
- When disabled, only owner and sudoers can add accounts

**Broadcast:**
- Send messages to all bot users
- Real-time progress tracking
- Success/failure statistics

### 5. User Features

**Regular Users:**
- Can add accounts (if enabled by owner)
- View their own accounts
- Cannot join channels or manage DB channels

## Database Collections

The bot uses MongoDB with these collections:

1. **users**: All users who started the bot
2. **accounts**: All added Telegram accounts
3. **sudoers**: List of sudoer user IDs
4. **db_channels**: DB channel configurations
5. **settings**: Bot settings (public_add_enabled, etc.)

## File Structure

```
telegram-bot-project/
├── bot.py                      # Main entry point
├── config.py                   # Environment configuration
├── database.py                 # MongoDB operations
├── helpers.py                  # Utility functions
├── keyboards.py                # UI keyboards
├── account_manager.py          # Account CRUD operations
├── join_manager.py             # Channel joining logic
├── handlers/
│   ├── __init__.py
│   ├── start.py               # /start command
│   ├── account_handlers.py    # Account management
│   ├── join_handlers.py       # Join operations
│   ├── admin_handlers.py      # Owner/Sudoer features
│   └── callback_handlers.py   # Navigation callbacks
├── requirements.txt            # Python dependencies
├── .env                        # Configuration
├── .gitignore                  # Git ignore rules
├── Procfile                    # Deployment config
└── runtime.txt                 # Python version
```

## Deployment

### Heroku Deployment

1. Create Heroku account
2. Install Heroku CLI
3. Login: `heroku login`
4. Create app: `heroku create your-app-name`
5. Add buildpack: `heroku buildpacks:add heroku/python`
6. Deploy:
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku master
```

### Railway Deployment

1. Create Railway account
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Configure environment variables
5. Deploy

### VPS Deployment

1. SSH into your VPS
2. Clone/Upload project
3. Install dependencies: `pip install -r requirements.txt`
4. Run with screen: `screen -S bot python bot.py`
5. Detach: `Ctrl+A+D`

## Security Notes

- Never share your `.env` file
- Keep session strings private
- Use strong 2FA passwords
- Regularly rotate bot tokens
- Monitor MongoDB access logs

## Troubleshooting

**Bot not starting:**
- Check Python version (3.11+)
- Verify all dependencies installed
- Check MongoDB connection

**Accounts not joining:**
- Check FloodWait delays
- Verify account sessions are valid
- Ensure DB channel is accessible

**Database errors:**
- Verify MongoDB URI is correct
- Check network connectivity
- Ensure MongoDB cluster is running

## Support

For issues or questions:
1. Check this guide first
2. Review error messages carefully
3. Verify all configurations
4. Check MongoDB connection

## License

Educational purposes only. Use responsibly.
