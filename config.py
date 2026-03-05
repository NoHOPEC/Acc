import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID"))
    MONGO_URI = os.getenv("MONGO_URI")
    
    API_ID = 38145963
    API_HASH = "9325201ac0b1f87528cede06dd88484d"
