import os
from dotenv import load_dotenv

# Load environment variables from .env file, if it exists
load_dotenv()

class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")  # Default to 0.0.0.0 for hosting
    PORT: int = int(os.getenv("PORT", "8000"))  # Default to 8000 for production
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/upload")
    
    # Sensitive information should be stored in environment variables (not hardcoded)
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/mydb")  # Set a default for local testing

settings = Settings()
