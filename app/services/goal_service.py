from app.models.goal_model import Goal, Savings
from mongoengine import DoesNotExist
from bson import ObjectId # type: ignore


class GoalsService:

    @staticmethod
    async def add_goals(goal_request):
        
        goal = Goal(
            title=goal_request.get("title"),
            description=goal_request.get("description"),
            target_date=goal_request.get("target_date"),
            target_amount=goal_request.get("target_amount"),
        )
        goal.save()
        return str(goal.id)
    
    async def delete_goals(alert_id: list):
        object_ids = [ObjectId(alert_id) for alert_id in alert_id]
        alerts = Goal.objects(id__in=object_ids)

        alerts.delete()
        return True
    

    async def all_goals():
        goals = Goal.objects()  
        
        result_goals = []
        for goal in goals:
            goal_dict = goal.to_mongo().to_dict()  

            if "_id" in goal_dict:
                goal_dict["_id"] = str(goal_dict["_id"]) 
            
            if "categories" in goal_dict:
                for category in goal_dict["categories"]:
                    if "_id" in category:
                        category["_id"] = str(category["_id"])  
                    
            result_goals.append(goal_dict)  
        
        return result_goals


    async def add_savings(entry_request):
        entry_amount = round(float(entry_request.get("entry_amount", 0.0)), 2)

        parent_goal_id = entry_request.get("parent_goal_id")

        try:
            # Check if the parent goal exists
            parent_goal = Goal.objects.get(id=parent_goal_id)
        except DoesNotExist:
            return {"error": "Parent goal not found"}

        savings = Savings(
            parent_goal_id=entry_request.get("parent_goal_id"),
            entry_amount=entry_request.get("entry_amount"),
            entry_date=entry_request.get("entry_date"),
        )
        savings.save()
        
        return str(savings.id)

    async def return_savings(goal_id):
        savings_entries = Savings.objects(parent_goal_id=goal_id)
        
        result_savings = []
        for savings in savings_entries:
            savings_dict = savings.to_mongo().to_dict() 
            savings_dict["_id"] = str(savings_dict["_id"])
            savings_dict["parent_goal_id"] = str(savings_dict["parent_goal_id"])
            result_savings.append(savings_dict)

        return result_savings

        