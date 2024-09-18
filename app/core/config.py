import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HOST: str = '0.0.0.0'
    PORT: int = 4000
    
    MONGO_URL: str = 'mongodb+srv://nelaykarmakar:0u7rxkmMOxmXJFjj@expensetracker.i0cqo.mongodb.net/'
settings = Settings()
