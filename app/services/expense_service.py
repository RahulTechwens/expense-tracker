from app.db.connection import mongodb
from app.models.expense_model import ExpenseRequest
from typing import List, Dict
from datetime import datetime, timedelta


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
    if len(categories) > 0:
        cursor = collection.find({"cat": {"$in": categories}})
    else:
        cursor = collection.find()
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


async def filter_sms_date_range(startDate, endDate):
    db = await mongodb.get_database()
    collection = db["demo_sms_data"]
 
    date_format = '%Y-%m-%d'
   
    # convert to datetime objects
    start_date = datetime.strptime(startDate, date_format)
    end_date = datetime.strptime(endDate, date_format)
   
    #end_date = end_date + timedelta(days=1)
   
    query = {
        "date": {
            "$gte": start_date.strftime('%Y-%m-%d'),
            "$lte": end_date.strftime('%Y-%m-%d')
        }
    }
 
    # find according to query
    cursor = collection.find(query)
    documents = await cursor.to_list(length=None)
 
    # Serialize documents
    serialized_data = []
    for doc in documents:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
        serialized_data.append(doc)
       
    return serialized_data
    
    
async def filter_sms_date(date):
    db = await mongodb.get_database()
    collection = db["demo_sms_data"]

    date_format = '%Y-%m-%d'
    
    # convert to datetime objects
    target_date = datetime.strptime(date, date_format)

    query = {
        "date": {
            "$eq": target_date.strftime('%Y-%m-%d')
        }
    }

    # find according to query
    cursor = collection.find(query)
    documents = await cursor.to_list(length=None)

    # Serialize the documents
    serialized_data = []
    for doc in documents:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
        serialized_data.append(doc)
       
    return serialized_data
