from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client.telegram_bot
        self.users = self.db.users
        self.accounts = self.db.accounts
        self.sudoers = self.db.sudoers
        self.db_channels = self.db.db_channels
        self.settings = self.db.settings

    async def add_user(self, user_id):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True
        )

    async def get_all_users(self):
        users = []
        async for user in self.users.find():
            users.append(user["user_id"])
        return users

    async def add_account(self, account_data):
        await self.accounts.insert_one(account_data)

    async def get_all_accounts(self):
        accounts = []
        async for account in self.accounts.find():
            accounts.append(account)
        return accounts

    async def delete_account(self, account_id):
        await self.accounts.delete_one({"_id": account_id})

    async def add_sudoer(self, user_id):
        await self.sudoers.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True
        )

    async def remove_sudoer(self, user_id):
        await self.sudoers.delete_one({"user_id": user_id})

    async def get_sudoers(self):
        sudoers = []
        async for sudoer in self.sudoers.find():
            sudoers.append(sudoer["user_id"])
        return sudoers

    async def is_sudoer(self, user_id):
        sudoer = await self.sudoers.find_one({"user_id": user_id})
        return sudoer is not None

    async def add_db_channel(self, channel_data):
        await self.db_channels.insert_one(channel_data)

    async def get_all_db_channels(self):
        channels = []
        async for channel in self.db_channels.find():
            channels.append(channel)
        return channels

    async def delete_db_channel(self, channel_id):
        await self.db_channels.delete_one({"_id": channel_id})

    async def get_setting(self, key):
        setting = await self.settings.find_one({"key": key})
        return setting["value"] if setting else None

    async def set_setting(self, key, value):
        await self.settings.update_one(
            {"key": key},
            {"$set": {"key": key, "value": value}},
            upsert=True
        )

db = Database()
