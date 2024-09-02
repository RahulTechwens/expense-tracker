from app.db.connection import mongodb
from app.models.expense_model import Expense
from typing import List, Dict
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q # type: ignore


async def insert_expense(expense_request):
    expense = Expense(
        cat=expense_request.get('cat'),
        merchant=expense_request.get('merchant'),
        acct=expense_request.get('acct'),
        bank=expense_request.get('bank'),
        date=expense_request.get('date'),
        body=expense_request.get('body'),
        amount=expense_request.get('amount'),
        type=expense_request.get('type'),
        method=expense_request.get('method'),
        manual=expense_request.get('manual'),
        keywords=expense_request.get('keywords'),
        vector=expense_request.get('vector'),
    )
    expense.save()
    return {"inserted_id": str(expense.id)}


async def filter_sms_category (categories: List[str], start_date, end_date):
    query = Q()
    if categories:
        query &= Q(cat__in=categories)
    if start_date and start_date:
        query &= Q(date__gte=start_date, date__lte=end_date)
    elif start_date:
        query &= Q(date__gte=start_date)
    elif end_date:
        query &= Q(date__lte=end_date)
    data = Expense.objects(query)
    if data.count() == 0:
        return []
    result = []
    for item in data:
        item_dict = item.to_mongo().to_dict()
        item_dict["_id"] = str(item_dict["_id"])
        result.append(item_dict)
    
    return result
        


# async def get_all_data ():
#     db = await mongodb.get_database()
#     collection = db["demo_sms_data"] 
#     cursor = collection.find({})
#     data = await cursor.to_list(length=None)
#     for item in data:
#         item["_id"] = str(item["_id"])
    
#     return data


# async def filter_sms_date_range(startDate, endDate):
#     db = await mongodb.get_database()
#     collection = db["demo_sms_data"]
 
#     date_format = '%Y-%m-%d'
   
#     # convert to datetime objects
#     start_date = datetime.strptime(startDate, date_format)
#     end_date = datetime.strptime(endDate, date_format)
   
#     #end_date = end_date + timedelta(days=1)
   
#     query = {
#         "date": {
#             "$gte": start_date.strftime('%Y-%m-%d'),
#             "$lte": end_date.strftime('%Y-%m-%d')
#         }
#     }
 
#     # find according to query
#     cursor = collection.find(query)
#     documents = await cursor.to_list(length=None)
 
#     # Serialize documents
#     serialized_data = []
#     for doc in documents:
#         if '_id' in doc:
#             doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
#         serialized_data.append(doc)
       
#     return serialized_data
    
    
# async def filter_sms_date(date):
#     db = await mongodb.get_database()
#     collection = db["demo_sms_data"]

#     date_format = '%Y-%m-%d'
    
#     # convert to datetime objects
#     target_date = datetime.strptime(date, date_format)

#     query = {
#         "date": {
#             "$eq": target_date.strftime('%Y-%m-%d')
#         }
#     }

#     # find according to query
#     cursor = collection.find(query)
#     documents = await cursor.to_list(length=None)

#     # Serialize the documents
#     serialized_data = []
#     for doc in documents:
#         if '_id' in doc:
#             doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
#         serialized_data.append(doc)
       
#     return serialized_data
