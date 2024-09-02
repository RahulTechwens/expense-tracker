from app.db.connection import mongodb
from app.models.alert_model import Alert
from app.models.expense_model import Cat
from typing import List, Dict
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q # type: ignore
from bson import ObjectId # type: ignore


days = [
    {"0":"Mon"},
    {"1":"TUe"},
    {"2":"Wed"},
    {"3":"Thu"},
    {"4":"Fri"},
    {"5":"Sat"},
    {"6":"Sun"},
]

months = [
    {"0":"Jan"},
    {"1":"Feb"},
    {"2":"Mar"},
    {"3":"Apr"},
    {"4":"May"},
    {"5":"Jun"},
    {"6":"Jul"},
    {"7":"Aug"},
    {"8":"Sep"},
    {"9":"Oct"},
    {"10":"Nov"},
    {"11":"Dec"},

]

async def insert_alert(dictData):
    if dictData.get('alert_type').lower() == 'daily':
        alert_data = [day for day in days if list(day.values())[0] in dictData.get('alert_data')]
    elif dictData.get('alert_type').lower() == 'monthly':
        alert_data = [month for month in months if list(months.values())[0] in dictData.get('alert_data')]
    print(alert_data)
    alert = Alert(
        alert_type = dictData.get('alert_type').lower(),
        alert_data = alert_data,
        limit = dictData.get('limit'),
        cat_ids = dictData.get('cat_ids'),
        status = dictData.get('status')
    )
    alert.save()
    return {"inserted_id": str(alert.id)}

async def check_categories(category_data: List['str']):
    object_ids = [ObjectId(id_) for id_ in category_data]
    categories = Cat.objects(id__in=object_ids)
    result_categories = []
    for category in categories:
        category_dict = category.to_mongo().to_dict()
        category_dict["_id"] = str(category_dict["_id"])
        result_categories.append(category_dict)
    
    return len(result_categories)