# app/database/connection.py

from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def get_database(self):
        return self.db

# Initialize the connection with database name
mongodb = MongoDB("mongodb+srv://nelaykarmakar:0u7rxkmMOxmXJFjj@expensetracker.i0cqo.mongodb.net/", "expenses")
