from app.models.goal_model import Goal, Savings
from mongoengine import DoesNotExist
from bson import ObjectId # type: ignore
from datetime import datetime, timedelta
from collections import defaultdict

class GoalsService:

    @staticmethod
    async def add_goals(goal_request, user):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
        goal = Goal(
            title=goal_request.get("title"),
            description=goal_request.get("description"),
            target_date=goal_request.get("target_date"),
            target_amount=goal_request.get("target_amount"),
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_phone = user['phone']
        )
        goal.save()
        return str(goal.id)
    
    async def delete_goals(goal_id, user):
        goal = Goal.objects(id=ObjectId(goal_id), user_phone=user['phone']).first()
        if goal:
            goal.delete()
            return True
        else:
            return False
    
    async def all_goals(goal_id, user):
        if goal_id:
            goal = Goal.objects(id=ObjectId(goal_id), user_phone=user['phone']).first()
            if goal:
                goal_dict = goal.to_mongo().to_dict()
                goal_dict["_id"] = str(goal_dict["_id"])
                savings_entries = Savings.objects(parent_goal_id=str(goal_dict.get("_id")))
                
                result_savings = []
                result_goals = []
                
                for savings in savings_entries:
                    savings_dict = savings.to_mongo().to_dict()
                    result_savings.append({
                        'entry_amount': savings_dict.get('entry_amount')
                    })
                if "_id" in goal_dict:
                    goal_dict["_id"] = str(goal_dict["_id"])
                total_savings = sum(s['entry_amount'] for s in result_savings if s['entry_amount'])
                goal_dict["amount_saved"] = float(total_savings)
                goal_dict["amount_saved_percentage"] = (total_savings / goal_dict.get('target_amount', 1)) * 100 

                return goal_dict
            else:
                return {}
        
        
        else:
            goals = Goal.objects(user_phone=user['phone']).order_by("-created_at")
            result_goals = []
            for goal in goals:
                goal_dict = goal.to_mongo().to_dict()
                savings_entries = Savings.objects(parent_goal_id=str(goal_dict.get("_id")))
                result_savings = []
                
                for savings in savings_entries:
                    savings_dict = savings.to_mongo().to_dict()
                    result_savings.append({
                        'entry_amount': savings_dict.get('entry_amount')
                    })
                if "_id" in goal_dict:
                    goal_dict["_id"] = str(goal_dict["_id"])
                total_savings = sum(s['entry_amount'] for s in result_savings if s['entry_amount'])
                goal_dict["amount_saved"] = float(total_savings)
                goal_dict["amount_saved_percentage"] = (total_savings / goal_dict.get('target_amount', 1)) * 100 
                result_goals.append(goal_dict)
            
            return result_goals

    async def add_savings(entry_request, user):
        entry_amount = round(float(entry_request.get("entry_amount", 0.0)), 2)

        parent_goal_id = entry_request.get("parent_goal_id")

        try:
            # Check if the parent goal exists
            parent_goal = Goal.objects.get(id=parent_goal_id,user_phone=user['phone'])
        except DoesNotExist:
            return {"error": "Parent goal not found"}

        savings = Savings(
            parent_goal_id=entry_request.get("parent_goal_id"),
            entry_amount=entry_request.get("entry_amount"),
            entry_date=entry_request.get("entry_date"),
            user_phone=user['phone']
        )
        savings.save()
        
        return str(savings.id)

    async def return_savings(goal_id, user):
        today = datetime.today()
        six_months_ago = today - timedelta(days=6 * 30)
        # end_date = today.strftime('%Y-%m-%d')
        # Define the date range as strings in YYYY-MM-DD format
        start_date = six_months_ago.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        savings_entries = Savings.objects(
            parent_goal_id=goal_id,
            entry_date__gte=start_date,
            entry_date__lte=end_date,
            user_phone=user['phone']
        )
        savings_by_month = defaultdict(float)
        for savings in savings_entries:
            entry_date = savings.entry_date if isinstance(savings.entry_date, datetime) else datetime.strptime(savings.entry_date, '%Y-%m-%d')
            entry_month = entry_date.strftime('%m')
            savings_by_month[entry_month] += savings.entry_amount
            

        result_savings = []
        for i in range(6, -1, -1):
            month = (today - timedelta(days=i * 30)).strftime('%m')
            result_savings.append({
                "entry_amount": savings_by_month.get(month, 0.0),
                "month": int(month)
        })
        
        return result_savings
    
    async def acheive(goal_id, request_data, user):
        goal =  Goal.objects(id=goal_id, user_phone=user['phone']).first()
        if not goal:
            return {"message": "Goal not found"}
        goal.status = request_data.get("status", goal.status)
        goal.save()

        return {"message": "Goal acheived successfully"}