import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    HOST = os.getenv("HOST", "127.0.0.1")  # Default host if not set
    PORT = int(os.getenv("PORT", "8004"))   # Convert port to integer
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "app/upload")  # Default upload directory if not set

settings = Settings()
