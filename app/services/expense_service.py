from app.db.connection import mongodb
from app.models.expense_model import Expense, Cat
from typing import List, Dict
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q # type: ignore
from fastapi.responses import JSONResponse # type: ignore



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


async def insert_cat(expense_request):
    cat = Cat(
        icon_id=expense_request.get('icon_id'),
        label=expense_request.get('label'),
    )
    cat.save()
    return {"inserted_id": str(cat.id)}


'''To find expenses into a specific date range '''
# async def filter_sms_category (categories: List[str], start_date, end_date):
#     query = Q()

#     # Filter by categories if provided
#     if categories:
#         query &= Q(cat__in=categories)
    
#     # Filter by date range if provided
#     if start_date and start_date:
#         query &= Q(date__gte=start_date, date__lte=end_date)
#     elif start_date:
#         query &= Q(date__gte=start_date)
#     elif end_date:
#         query &= Q(date__lte=end_date)
    
#     # Fetch the data based on the constructed query
#     data = Expense.objects(query)
    
#     # If no data is found, return an empty list
#     if data.count() == 0:
#         return []

#     # Convert the documents to a list of dictionaries
#     result = []
#     for item in data:
#         item_dict = item.to_mongo().to_dict()
#         item_dict["_id"] = str(item_dict["_id"])
#         result.append(item_dict)
    
#     return result
'''end'''        


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


def get_sum_amount(start_time, end_time):
    query = Q()
    
    query &= Q(date__gte=start_time, date__lte=end_time)
    
    data = Expense.objects(query)
    
    if data.count() == 0:
        return [], []

    result = []
    for item in data:
        item_dict = item.to_mongo().to_dict()
        item_dict["_id"] = str(item_dict["_id"])
        result.append(item_dict)
    total = 0
    # Calculate unique categories with counts and sums
    category_summary = {}
    for item in data:
        cat = item.cat
        if cat not in category_summary:
            category_summary[cat] = {"count": 0, "sum": 0}
        category_summary[cat]["count"] += 1
        category_summary[cat]["sum"] += item.amount
        total = total + item.amount
    
    unique_cats = list(category_summary.keys())
    category_counts_sums = [
        {"category": cat, "count": details["count"], "expense": details["sum"], }
        for cat, details in category_summary.items()
    ]
    
    summary_result = {
        "Total": total,
        "Categories": category_counts_sums
    }
    
    return summary_result


async def filter_sms_category(categories: List[str], start_date, end_date):
    query = Q()

    if categories:
        query &= Q(cat__in=categories)
        #Fetch the data based on the constructed query
        data = Expense.objects(query)
        
        # If no data is found, return an empty list
        if data.count() == 0:
            return []

        # Convert the documents to a list of dictionaries
        result = []
        for item in data:
            item_dict = item.to_mongo().to_dict()
            item_dict["_id"] = str(item_dict["_id"])
            result.append(item_dict)
        
        return JSONResponse(
            status_code=200,
            content={"Message": "Data Fetched Successfully", "Entered Categories":categories, "Filtered Data": result}
        )
    
    
    if start_date and end_date:
        
        category_counts_sums = get_sum_amount(start_date,end_date)
        #return unique_cats, result, category_counts_sums
        #return category_counts_sums
        
        #prevous day starting and ending
        start_datetime = datetime.fromisoformat(start_date)
        starting_datetime = start_datetime - timedelta(days=1)
        start_date2 = starting_datetime.isoformat()
        
        end_datetime = datetime.fromisoformat(end_date)
        ending_datetime = end_datetime - timedelta(days=1)
        end_date2 = ending_datetime.isoformat()
        
        category_counts_sums2 = get_sum_amount(start_date2,end_date2)

        # return [{
        #     "Message": "Data Fetched Successfully",
        #     #   "Entered Categories": unique_cats,
        #     "Time Span": f"{start_date} to {end_date}",
        #     #   "Filtered Data": result,
        #     "Category Summary": result
        # }]
        
        return [
            {
                "Message": "Data Fetched Successfully",
                "Time Spans": [
                    {
                        "Time Span": f"{start_date} to {end_date}",
                        "Summary": category_counts_sums
                    },
                
                    {
                        "Time Span": f"{start_date2} to {end_date2}",
                        "Summary": category_counts_sums2
                    }
                ]
            }
        ]
