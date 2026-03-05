from pyrogram import Client
from config import Config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

bot = Client(
    "account_manager_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

if __name__ == "__main__":
    logger.info("Starting Account Manager Bot...")
    bot.run()
