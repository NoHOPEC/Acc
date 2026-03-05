import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID"))
    MONGO_URI = os.getenv("MONGO_URI")
    
    API_ID = 6
    API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
