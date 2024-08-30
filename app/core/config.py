import os
from dotenv import load_dotenv # type: ignore
load_dotenv()

class Settings:
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8004"))
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "app/upload")
    MONGO_URL = os.getenv("MONGO_URL", 'mongodb+srv://nelaykarmakar:0u7rxkmMOxmXJFjj@expensetracker.i0cqo.mongodb.net/')
settings = Settings()
