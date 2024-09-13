import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HOST: str = os.getenv("HOST")
    PORT: int = int(os.getenv("PORT"))
    
    MONGO_URL: str = os.getenv("MONGO_URL")
settings = Settings()
