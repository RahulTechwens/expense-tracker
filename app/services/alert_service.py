from app.db.connection import mongodb
from app.models.alert_model import Alert
from app.models.expense_model import Cat
from typing import List, Dict
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q # type: ignore
from bson import ObjectId # type: ignore
from fastapi import FastAPI, HTTPException, Query
from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.db.connection import MongoDB






class AlertService:
    
    
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

    async def insert_alert(self, dictData):
        if dictData.get('alert_type').lower() == 'daily':
            alert_data = [day for day in self.days if list(day.values())[0] in dictData.get('alert_data')]
        elif dictData.get('alert_type').lower() == 'monthly':
            alert_data = [month for month in self.months if list(self.months.values())[0] in dictData.get('alert_data')]
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
        if not category_data:
            return []
        object_ids = [icon_id for icon_id in category_data]
        categories = Cat.objects(icon_id__in=object_ids)
        result_categories = []
        for category in categories:
            category_dict = category.to_mongo().to_dict()
            category_dict["_id"] = str(category_dict["_id"])
            result_categories.append(category_dict)
        
        return len(result_categories)

    async def all_alerts():
        alerts = Alert.objects.aggregate([
            {
                "$lookup": {
                    "from": "categories",  # Collection name for categories
                    "localField": "cat_ids",  # Field in Alert referencing categories
                    "foreignField": "icon_id",  # Field in Cat (category model) referencing ids
                    "as": "categories"  # Result will be stored in this field
                }
            }
        ])

        result_alerts = []
        for alert in alerts:
            if "_id" in alert:
                alert["_id"] = str(alert["_id"])  # Convert ObjectId to string
            if "categories" in alert:
                for category in alert["categories"]:
                    if "_id" in category:
                        category["_id"] = str(category["_id"])  # Convert ObjectId for category too
            result_alerts.append(alert)

        return result_alerts


    async def toggle_alert_status(alert_id: str, status: bool):
        try:
            alert = Alert.objects(id=alert_id).first()
            if not alert:
                return {"message": "Alert not found"}
            alert.status = status
            alert.save()
            return alert._id
        except Exception as e:
            return {"message": f"Error updating alert: {e}"}
        
    async def delete_alert(alert_id: list):
        object_ids = [ObjectId(alert_id) for alert_id in alert_id]
        alerts = Alert.objects(id__in=object_ids)
        # print(object_ids)
        alerts.delete()
        return True