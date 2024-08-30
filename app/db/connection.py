from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from app.core.config import settings
class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def get_database(self):
        return self.db

mongodb = MongoDB(settings.MONGO_URL, "expenses")
