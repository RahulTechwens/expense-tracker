# from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from mongoengine import connect
from app.core.config import settings
class MongoDB:
    def __init__(self, uri: str, db_name: str):
    # Define the default connection using mongoengine
        connect(db_name, host=uri)

    async def get_database(self):
        return self.db

mongodb = MongoDB(settings.MONGO_URL, "expenses")
