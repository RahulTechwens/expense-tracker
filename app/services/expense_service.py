from app.db.connection import mongodb
from app.models.expense_model import ExpenseRequest
from typing import List, Dict


async def insert_expense(amount:str, description:str):
    db = await mongodb.get_database()
    collection = db["expenses"]
    document = {
        "amount": amount,
        "description": description,
    }
    insert_result = await collection.insert_one(document)
    return {"inserted_id": str(insert_result.inserted_id)}


async def filter_sms_category (categories: List[str]):
    db = await mongodb.get_database()
    collection = db["demo_sms_data"]
    cursor = collection.find({"cat": {"$in": [categories]}})
    data = await cursor.to_list(length=None)
    for item in data:
        item["_id"] = str(item["_id"])
    
    return data


async def get_all_data ():
    db = await mongodb.get_database()
    collection = db["demo_sms_data"] 
    cursor = collection.find({})
    data = await cursor.to_list(length=None)
    for item in data:
        item["_id"] = str(item["_id"])
    
    return data
