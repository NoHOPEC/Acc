# System Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Telegram Bot API                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                        bot.py                                │
│                   (Main Entry Point)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│   config.py      │  │   database.py    │
│  (Environment)   │  │   (MongoDB)      │
└──────────────────┘  └──────────────────┘
          │                     │
          └──────────┬──────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Handlers Layer                          │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐│
│  │  start.py │ │ account_  │ │  join_    │ │   admin_    ││
│  │           │ │ handlers  │ │ handlers  │ │  handlers   ││
│  └───────────┘ └───────────┘ └───────────┘ └─────────────┘│
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ account_manager  │  │  join_manager    │
│     .py          │  │      .py         │
└──────────────────┘  └──────────────────┘
          │                     │
          └──────────┬──────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Utility Layer                              │
│  ┌───────────┐ ┌───────────┐                               │
│  │helpers.py │ │keyboards  │                               │
│  │           │ │   .py     │                               │
│  └───────────┘ └───────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Message
     │
     ▼
Handler (start.py, account_handlers.py, etc.)
     │
     ▼
Permission Check (helpers.py)
     │
     ├─ Authorized ──────────────┐
     │                            ▼
     │                      Manager Layer
     │                      (account_manager.py)
     │                            │
     │                            ▼
     │                      Database Operation
     │                      (database.py)
     │                            │
     │                            ▼
     │                        MongoDB
     │                            │
     └─ Unauthorized ─────────────┤
                                  ▼
                            Response to User
```

## Database Schema

```
┌──────────────────────────────────────────────────────────┐
│                      MongoDB                              │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   users     │  │  accounts   │  │  sudoers    │     │
│  │             │  │             │  │             │     │
│  │ • user_id   │  │ • type      │  │ • user_id   │     │
│  │             │  │ • session   │  │             │     │
│  │             │  │ • phone     │  │             │     │
│  │             │  │ • user_id   │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │db_channels  │  │  settings   │                       │
│  │             │  │             │                       │
│  │ • name      │  │ • key       │                       │
│  │ • username  │  │ • value     │                       │
│  │             │  │             │                       │
│  └─────────────┘  └─────────────┘                       │
└──────────────────────────────────────────────────────────┘
```

## User Flow Diagrams

### Adding Account Flow

```
User clicks "➕ Add Account"
         │
         ▼
Select Method
         │
    ┌────┼────┐
    ▼    ▼    ▼
Pyrogram│Telethon│Direct Login
    │    │    │
    │    │    ├─► Enter Phone
    │    │    ├─► Receive OTP
    │    │    ├─► Enter OTP
    │    │    └─► Enter 2FA (if needed)
    │    │
    └────┴────┘
         │
         ▼
Validate Session
         │
         ▼
Store in MongoDB
         │
         ▼
Success Message
```

### Joining Channels Flow

```
User clicks "🔗 Join Channels"
         │
         ▼
Select Mode (All/Specific)
         │
    ┌────┴────┐
    ▼         ▼
Join All  Join Specific
    │         │
    │         └─► Enter Range (100-200)
    │
    └────┬────┘
         │
         ▼
Select DB Channel
         │
         ▼
Select Join Type (Groups/Channels/Both)
         │
         ▼
Fetch Links from DB Channel
         │
         ▼
For each Account:
    For each Link:
        ├─► Check if already member
        ├─► Join channel/group
        ├─► Wait 3 seconds
        └─► Update progress
         │
         ▼
Show Results (Success/Failed/Already Member)
```

### Owner Management Flow

```
Owner clicks "👥 Manage Sudoers"
         │
         ▼
View Sudoer List
         │
    ┌────┴────┐
    ▼         ▼
Add New   Select Existing
    │         │
    │         └─► View Details
    │         │
    │         └─► Remove Sudoer
    │
    └─► Enter User ID
    │
    └─► Add to Database
    │
    └─► Success Message
```

## Session Management

```
┌──────────────────────────────────────────────────────┐
│                 Session Types                         │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  Pyrogram    │  │  Telethon    │                 │
│  │  Session     │  │  Session     │                 │
│  │              │  │              │                 │
│  │ String based │  │ String based │                 │
│  │ MTProto      │  │ MTProto      │                 │
│  └──────────────┘  └──────────────┘                 │
│                                                       │
│         Stored in MongoDB                            │
│                │                                      │
│                ▼                                      │
│    ┌─────────────────────┐                          │
│    │  Encrypted Storage  │                          │
│    │  • session_string   │                          │
│    │  • phone            │                          │
│    │  • user_id          │                          │
│    │  • type             │                          │
│    └─────────────────────┘                          │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## Permission System

```
┌──────────────────────────────────────────────────────┐
│                 Access Hierarchy                      │
│                                                       │
│              ┌─────────────┐                         │
│              │   OWNER     │                         │
│              │  (ID: XXXX) │                         │
│              └──────┬──────┘                         │
│                     │                                 │
│        ┌────────────┴────────────┐                   │
│        ▼                         ▼                    │
│  ┌──────────┐             ┌──────────┐              │
│  │ SUDOERS  │             │  USERS   │              │
│  │ (Added)  │             │  (Any)   │              │
│  └──────────┘             └──────────┘              │
│        │                         │                    │
│        │                         │                    │
│  Can manage:              Can:                       │
│  • Accounts               • Add accounts (if enabled)│
│  • DB Channels            • View own accounts        │
│  • Join operations        • Basic features           │
│        │                         │                    │
│  Cannot:                  Cannot:                    │
│  • Manage sudoers         • Manage anything          │
│  • Broadcast              • Admin features           │
│  • Settings               • Join operations          │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────────┐
│               Production Environment                  │
│                                                       │
│  ┌────────────────────────────────────────────┐     │
│  │           Cloud Platform                    │     │
│  │  (Heroku / Railway / VPS)                  │     │
│  │                                             │     │
│  │  ┌──────────────────────────────────┐      │     │
│  │  │        Bot Instance              │      │     │
│  │  │                                  │      │     │
│  │  │  ├─ bot.py (Main Process)       │      │     │
│  │  │  ├─ Handlers (Event Listeners)  │      │     │
│  │  │  ├─ Managers (Business Logic)   │      │     │
│  │  │  └─ Database (Connection Pool)  │      │     │
│  │  │            │                     │      │     │
│  │  └────────────┼─────────────────────┘      │     │
│  │               │                             │     │
│  └───────────────┼─────────────────────────────┘     │
│                  │                                    │
│                  ▼                                    │
│  ┌────────────────────────────────────────────┐     │
│  │         MongoDB Atlas                       │     │
│  │         (Cloud Database)                    │     │
│  │                                             │     │
│  │  • Persistent Storage                      │     │
│  │  • Auto Backup                             │     │
│  │  • High Availability                       │     │
│  └─────────────────────────────────────────────┘     │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
User Action
    │
    ▼
Try Operation
    │
    ├─ Success ──────► Success Message
    │
    └─ Error
         │
         ├─ FloodWait ───► Wait & Retry
         │
         ├─ Already Member ──► Skip & Continue
         │
         ├─ Invalid Session ──► Error Message
         │
         └─ Unknown Error ──► Log & Notify User
```

## State Management

```
┌──────────────────────────────────────────────────────┐
│              State Storage                            │
│                                                       │
│  ┌────────────────┐      ┌────────────────┐         │
│  │  user_states   │      │  join_states   │         │
│  │  (In Memory)   │      │  (In Memory)   │         │
│  │                │      │                │         │
│  │ • User ID      │      │ • User ID      │         │
│  │ • Action       │      │ • Mode         │         │
│  │ • Data         │      │ • Channel      │         │
│  └────────────────┘      └────────────────┘         │
│                                                       │
│  Used for multi-step operations                      │
│  Cleared after completion                            │
│                                                       │
└──────────────────────────────────────────────────────┘
```
