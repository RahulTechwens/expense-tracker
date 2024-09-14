import os
from mongoengine import connect
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        connect(db_name, host=uri)
        print(f"Connected to {uri}/{db_name}")

    async def get_database(self):
        return self.db

mongodb = MongoDB(os.getenv("MONGODB_URL"), 'expenses')
