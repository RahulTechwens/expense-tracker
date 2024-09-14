from app.db.connection import mongodb
from app.models.expense_model import Expense, Cat, Message, CustomCat
from typing import List
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q  # type: ignore
from mongoengine import ValidationError
from fastapi.responses import JSONResponse  # type: ignore
from concurrent.futures import ThreadPoolExecutor
from mongoengine import DoesNotExist
import asyncio
from collections import defaultdict

class ExpenseService:

    @staticmethod
    async def insert_expense(expense_request):
        def save_expense():
            expense = Expense(
                cat=expense_request.get("cat"),
                merchant=expense_request.get("merchant"),
                acct=expense_request.get("acct"),
                bank=expense_request.get("bank"),
                date=expense_request.get("date"),
                body=expense_request.get("body"),
                amount=expense_request.get("amount"),
                type=expense_request.get("type"),  # Debit | Credit
                method=expense_request.get(
                    "method"
                ),  #  default Cash, UPI, Bank Transfer
                manual=expense_request.get("manual"),
                keywords=expense_request.get("keywords"),
                vector=expense_request.get("vector"),
            )
            expense.save()
            return str(expense.id)
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            inserted_id = await loop.run_in_executor(pool, save_expense)
        return {"inserted_id": inserted_id}

    @staticmethod
    async def insert_custom_cat(expense_request):
        parent_genre_id = expense_request.get("parent_genre_id")
        try:
            is_parent = Cat.objects.get(id=parent_genre_id)
            label = expense_request.get("label")
            existing_cat = Cat.objects(label=label).first()
            existing_custom_cat = CustomCat.objects(label=label).first()
            
            if existing_cat or existing_custom_cat:
                raise ValidationError(f"The label '{label}' already exists.")
            else:

                def save_cat():
                    cat = CustomCat(
                        icon_id=expense_request.get("icon_id"),
                        label=expense_request.get("label"),
                        parent_genre_id=expense_request.get("parent_genre_id"),
                    )
                    cat.save()
                    return str(cat.id)

                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as pool:
                    inserted_id = await loop.run_in_executor(pool, save_cat)

                return {"inserted_id": inserted_id}

        except DoesNotExist:
            raise ValueError(
                f"Parent category with id '{parent_genre_id}' does not exist."
            )

    @staticmethod
    async def filter_sms_category(
        category_ids: List[str], start_date, end_date, group_by
    ):
        cats = Cat.objects(id__in=category_ids).only("label")
        cat_dict = {str(cat.id): cat.label for cat in cats}
        categories = [cat_dict.get(cat_id, "Unknown") for cat_id in category_ids]
        query = Q()
        result = []
        if categories:
            query &= Q(cat__in=categories)
            data = Expense.objects(query)
            if data.count() == 0:
                return []
            for item in data:
                item_dict = item.to_mongo().to_dict()
                item_dict["_id"] = str(item_dict["_id"])
                result.append(item_dict)

        elif start_date and end_date:
            categories = Cat.objects()
            start_datetime = datetime.fromisoformat(start_date)
            starting_datetime = start_datetime - timedelta(days=1)
            previous_day_start_date = starting_datetime.isoformat()
            end_datetime = datetime.fromisoformat(end_date)
            ending_datetime = end_datetime - timedelta(days=1)
            previous_day_end_date = ending_datetime.isoformat()
            total_expense = 0
            previous_total_expense = 0
            for category in categories:
                label = category.label
                expenses = Expense.objects(
                    Q(cat=label) & Q(date__gte=start_date) & Q(date__lte=end_date)
                )
                total_amount = sum(expense.amount for expense in expenses)
                total_expense = total_expense + total_amount
                previous_day_expenses = Expense.objects(
                    Q(cat=label)
                    & Q(date__gte=previous_day_start_date)
                    & Q(date__lte=previous_day_end_date)
                )
                previous_total_amount = sum(
                    previous_day_expense.amount
                    for previous_day_expense in previous_day_expenses
                )
                previous_total_expense = previous_total_expense + previous_total_amount
                result.append(
                    {
                        "category": label,
                        "amount": total_amount,
                        "previous_amount": previous_total_amount,
                    }
                )
        elif group_by:
            if group_by == "all":
                data = Expense.objects()
                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])
                    result.append(item_dict)

            elif group_by == "category":
                result = []
                data = Expense.objects()
                categorized_expenses = {}

                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])
                    category = item_dict.get("cat")
                    if category not in categorized_expenses:
                        categorized_expenses[category] = {
                            "headerName": category,
                            "innerData": []
                        }
                    categorized_expenses[category]["innerData"].append(item_dict)
                result = list(categorized_expenses.values())

            elif group_by == "merchant":
                result = []
                data = Expense.objects()
                grouped_by_merchant = {}

                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])
                    merchant = item_dict.get("merchant")
                    if merchant not in grouped_by_merchant:
                        grouped_by_merchant[merchant] = {
                            "headerName": merchant,
                            "innerData": []
                        }
                    grouped_by_merchant[merchant]["innerData"].append(item_dict)
                result = list(grouped_by_merchant.values())

            # Return result
            content ={
                    "message": "All Data Fetched Successfully",
                    "data": result,
                }
            return content

        else:
            data = Expense.objects()

            for item in data:
                item_dict = item.to_mongo().to_dict()
                item_dict["_id"] = str(item_dict["_id"])
                result.append(item_dict)

        # Return result
        content = (
            {
                "message": "All Data Fetched Successfully",
                "data": result,
            },
        )
        return content

    @staticmethod
    async def expense_gpt_msg(expense_request):
        message = Message(
            msg=expense_request.get("msg"),
        )
        return {message}

    @staticmethod
    async def show_all_cat():
        data = Cat.objects()
        result = []
        for item in data:
            item_dict = item.to_mongo().to_dict()
            item_dict["_id"] = str(item_dict["_id"])
            result.append(item_dict)

        return result

    @staticmethod
    async def rename_custom_cat(rename_request):
        id = rename_request.get("id")
        new_label = rename_request.get("new_label")
        cat = CustomCat.objects(id=id).first()
        if cat:
            cat.label = new_label
            cat.save()
        return new_label

    @staticmethod
    async def time_wise_expense(request_data):
        time_type = request_data.get("time_type")
        index = request_data.get("index")
        type = request_data.get("type")
        query = Q()
        result = []

        if time_type == "daily":
            date = index
            query &= Q(date=date)
            data = Expense.objects(query)
            if data.count() == 0:
                return []

            result = []
            for item in data:
                item_dict = item.to_mongo().to_dict()
                item_dict["_id"] = str(item_dict["_id"])
                result.append(item_dict)
                
            if type == "category":
                categorized_expenses = {}
                for item in result:
                    category = item.get("cat")
                    
                    if category not in categorized_expenses:
                        categorized_expenses[category] = {
                            "headerName": category,
                            "innerData": []
                        }
                    categorized_expenses[category]["innerData"].append(item)
                
                result = list(categorized_expenses.values())

                
            elif type == "merchant":
                categorized_expenses = {}
                
                for item in result:
                    category = item.get("cat")
                    merchant = item.get("merchant")
                    
                    if merchant not in categorized_expenses:
                        categorized_expenses[merchant] = {
                            "headerName": merchant,
                            "innerData": []
                        }
                    categorized_expenses[merchant]["innerData"].append(item)
                result = list(categorized_expenses.values())    
            

        elif time_type == "monthly":
            from datetime import datetime

            # Get the current year
            current_year = datetime.now().year
            if index == "01":
                start_date = f"{current_year}-01-01"
                end_date = f"{current_year}-01-31"
            if index == "02":
                start_date = f"{current_year}-02-01"
                end_date = f"{current_year}-02-28"
            if index == "03":
                start_date = f"{current_year}-03-01"
                end_date = f"{current_year}-03-30"
            if index == "04":
                start_date = f"{current_year}-04-02"
                end_date = f"{current_year}-04-30"
            if index == "05":
                start_date = f"{current_year}-05-02"
                end_date = f"{current_year}-05-30"
            if index == "06":
                start_date = f"{current_year}-06-02"
                end_date = f"{current_year}-06-30"
            if index == "07":
                start_date = f"{current_year}-07-02"
                end_date = f"{current_year}-07-30"
            if index == "08":
                start_date = f"{current_year}-08-02"
                end_date = f"{current_year}-08-30"
            if index == "09":
                start_date = f"{current_year}-09-01"
                end_date = f"{current_year}-09-30"
            if index == "10":
                start_date = f"{current_year}-10-02"
                end_date = f"{current_year}-10-30"
        
        
        
        
        
            date = index
            # Assuming 'date' is the field you want to filter by
            query = Q(date__gte=start_date) & Q(date__lte=end_date)

            # Fetch the data based on the constructed query
            data = Expense.objects(query)

            # If no data is found, return an empty list
            if data.count() == 0:
                return []

            result = []
            for item in data:
                item_dict = item.to_mongo().to_dict()
                item_dict["_id"] = str(item_dict["_id"])
                result.append(item_dict)
                
            if type == "category":
                categorized_expenses = {}

                for item in result:
                    category = item.get("cat")
                    
                    if category not in categorized_expenses:
                        categorized_expenses[category] = {
                            "headerName": category,
                            "innerData": []
                        }
                    categorized_expenses[category]["innerData"].append(item)
                
                result = list(categorized_expenses.values())

                
            elif type == "merchant":
                categorized_expenses = {}
                
                for item in result:
                    category = item.get("cat")
                    merchant = item.get("merchant")
                    
                    if merchant not in categorized_expenses:
                        categorized_expenses[merchant] = {
                            "headerName": merchant,
                            "innerData": []
                        }
                    categorized_expenses[merchant]["innerData"].append(item)
                result = list(categorized_expenses.values())
        # Return result
        content = {
                "message": "All Data Fetched Successfully",
                "data": result,
            }
        return content