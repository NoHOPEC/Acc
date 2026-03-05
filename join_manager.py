from pyrogram import Client
from pyrogram.errors import FloodWait, UserAlreadyParticipant, InviteHashExpired
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserAlreadyParticipantError
import asyncio
import re
from database import db
from account_manager import account_manager

class JoinManager:
    def __init__(self):
        self.join_delay = 3

    async def fetch_links_from_channel(self, bot, channel_username, start_id=None, end_id=None):
        links = []
        try:
            if channel_username.startswith("+") or len(channel_username) > 20:
                try:
                    chat = await bot.join_chat(channel_username)
                    chat_id = chat.id
                except:
                    chat_id = channel_username
            else:
                if not channel_username.startswith("@"):
                    channel_username = f"@{channel_username}"
                chat_id = channel_username
            
            message_count = 0
            async for message in bot.get_chat_history(chat_id):
                message_count += 1
                
                if start_id and end_id:
                    if message.id < start_id or message.id > end_id:
                        continue
                elif start_id:
                    if message.id != start_id:
                        continue
                
                if message.text:
                    found_links = self.extract_links(message.text)
                    links.extend(found_links)
                
                if message.caption:
                    found_links = self.extract_links(message.caption)
                    links.extend(found_links)
            
            print(f"Checked {message_count} messages, found {len(links)} links")
            
        except Exception as e:
            print(f"Error fetching links: {e}")
        
        return links

    def extract_links(self, text):
        pattern = r'https?://(?:t\.me|telegram\.me|telegram\.dog)/(?:joinchat/)?([^\s]+)'
        matches = re.findall(pattern, text)
        return [f"https://t.me/{match}" if not match.startswith('joinchat') else f"https://t.me/joinchat/{match}" for match in matches]

    def categorize_link(self, link):
        if '/joinchat/' in link or '/+' in link:
            return 'group'
        else:
            return 'channel'

    async def join_with_pyrogram(self, client, link):
        try:
            await client.start()
            
            if '/joinchat/' in link or '/+' in link:
                invite_hash = link.split('/')[-1]
                await client.join_chat(invite_hash)
            else:
                username = link.split('/')[-1]
                await client.join_chat(username)
            
            await client.stop()
            return True, "Joined successfully"
        except UserAlreadyParticipant:
            await client.stop()
            return False, "Already a member"
        except FloodWait as e:
            await client.stop()
            return False, f"FloodWait: {e.value} seconds"
        except InviteHashExpired:
            await client.stop()
            return False, "Invite link expired"
        except Exception as e:
            await client.stop()
            return False, str(e)

    async def join_with_telethon(self, client, link):
        try:
            await client.connect()
            
            if '/joinchat/' in link or '/+' in link:
                invite_hash = link.split('/')[-1]
                await client(JoinChatRequest(invite_hash))
            else:
                username = link.split('/')[-1]
                await client(JoinChannelRequest(username))
            
            await client.disconnect()
            return True, "Joined successfully"
        except UserAlreadyParticipantError:
            await client.disconnect()
            return False, "Already a member"
        except FloodWaitError as e:
            await client.disconnect()
            return False, f"FloodWait: {e.seconds} seconds"
        except Exception as e:
            await client.disconnect()
            return False, str(e)

    async def join_links(self, accounts, links, join_type="both", progress_callback=None):
        total_links = len(links)
        total_accounts = len(accounts)
        
        results = {
            "success": 0,
            "failed": 0,
            "already_member": 0,
            "details": []
        }
        
        for acc_idx, account in enumerate(accounts):
            client = await account_manager.get_client(account)
            if not client:
                continue
            
            for link_idx, link in enumerate(links):
                link_type = self.categorize_link(link)
                
                if join_type == "groups" and link_type != "group":
                    continue
                elif join_type == "channels" and link_type != "channel":
                    continue
                
                if account.get("type") == "pyrogram":
                    success, message = await self.join_with_pyrogram(client, link)
                else:
                    success, message = await self.join_with_telethon(client, link)
                
                if success:
                    results["success"] += 1
                elif "already" in message.lower():
                    results["already_member"] += 1
                else:
                    results["failed"] += 1
                
                results["details"].append({
                    "account": account.get("phone"),
                    "link": link,
                    "status": message
                })
                
                if progress_callback:
                    progress = ((acc_idx * total_links + link_idx + 1) / (total_accounts * total_links)) * 100
                    await progress_callback(progress, acc_idx + 1, total_accounts, link_idx + 1, total_links)
                
                await asyncio.sleep(self.join_delay)
        
        return results

join_manager = JoinManager()
