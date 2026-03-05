from pyrogram import Client
from telethon import TelegramClient
from telethon.sessions import StringSession
from database import db
import asyncio

class AccountManager:
    def __init__(self):
        self.clients = {}

    async def add_pyrogram_session(self, session_string, user_id):
        try:
            from config import Config
            client = Client(
                f"account_{user_id}",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                session_string=session_string
            )
            
            await client.start()
            me = await client.get_me()
            
            account_data = {
                "type": "pyrogram",
                "session_string": session_string,
                "phone": me.phone_number,
                "user_id": me.id,
                "session_name": f"account_{user_id}",
                "added_by": user_id
            }
            
            await db.add_account(account_data)
            await client.stop()
            
            return True, f"Account {me.phone_number} added successfully!"
        except Exception as e:
            return False, f"Error adding Pyrogram session: {str(e)}"

    async def add_telethon_session(self, session_string, user_id):
        try:
            from config import Config
            client = TelegramClient(
                StringSession(session_string),
                Config.API_ID,
                Config.API_HASH
            )
            
            await client.connect()
            me = await client.get_me()
            
            account_data = {
                "type": "telethon",
                "session_string": session_string,
                "phone": me.phone,
                "user_id": me.id,
                "session_name": f"account_{user_id}",
                "added_by": user_id
            }
            
            await db.add_account(account_data)
            await client.disconnect()
            
            return True, f"Account {me.phone} added successfully!"
        except Exception as e:
            return False, f"Error adding Telethon session: {str(e)}"

    async def create_direct_login(self, phone, code, password=None):
        try:
            from config import Config
            client = Client(
                f"direct_{phone}",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH
            )
            
            await client.connect()
            
            if password:
                await client.sign_in(phone, code, password=password)
            else:
                await client.sign_in(phone, code)
            
            me = await client.get_me()
            session_string = await client.export_session_string()
            
            account_data = {
                "type": "pyrogram",
                "session_string": session_string,
                "phone": me.phone_number,
                "user_id": me.id,
                "session_name": f"direct_{phone}",
                "added_by": me.id
            }
            
            await db.add_account(account_data)
            await client.stop()
            
            return True, f"Account {me.phone_number} logged in successfully!"
        except Exception as e:
            return False, f"Error during direct login: {str(e)}"

    async def get_client(self, account):
        account_type = account.get("type")
        session_string = account.get("session_string")
        
        try:
            from config import Config
            if account_type == "pyrogram":
                client = Client(
                    account.get("session_name"),
                    api_id=Config.API_ID,
                    api_hash=Config.API_HASH,
                    session_string=session_string
                )
            elif account_type == "telethon":
                client = TelegramClient(
                    StringSession(session_string),
                    Config.API_ID,
                    Config.API_HASH
                )
            else:
                return None
            
            return client
        except Exception as e:
            print(f"Error getting client: {e}")
            return None

account_manager = AccountManager()
