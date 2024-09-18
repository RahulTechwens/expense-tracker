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
from calendar import monthrange
from mongoengine.queryset.visitor import Q
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
        print(categories)
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
        content = {
                "message": "All Data Fetched Successfully",
                "data": result,
            }
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
                    cat_obj = Cat.objects(Q(label=category)).first()
                    cat_id = str(cat_obj.id )if cat_obj else None
                    if category not in categorized_expenses:
                        categorized_expenses[category] = {
                            "headerName": category,
                            "cat_id":cat_id,
                            "innerData": []
                        }
                    categorized_expenses[category]["innerData"].append(item)
                
                result = list(categorized_expenses.values())

            elif type == "merchant":
                categorized_expenses = {}
                
                for item in result:
                    category = item.get("cat")
                    merchant = item.get("merchant")
                    # cat_obj = Cat.objects(Q(label=category)).first()
                    # cat_id = str(cat_obj.id )if cat_obj else None
                    if merchant not in categorized_expenses:
                        categorized_expenses[merchant] = {
                            "headerName": merchant,
                            "cat_id":item.get("merchant_slug"),
                            "innerData": []
                        }
                    categorized_expenses[merchant]["innerData"].append(item)
                result = list(categorized_expenses.values())

        elif time_type == "monthly":
            try:
                month = int(index) + 1
                current_year = datetime.now().year
                start_date = f"{current_year}-{month:02d}-01"
                _, last_day = monthrange(current_year, month)
                end_date = f"{current_year}-{month:02d}-{last_day:02d}"

                query = Q(date__gte=start_date) & Q(date__lte=end_date)
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
                        cat_obj = Cat.objects(Q(label=category)).first()
                        cat_id = str(cat_obj.id )if cat_obj else None
                        if category not in categorized_expenses:
                            categorized_expenses[category] = {
                                "headerName": category,
                                "cat_id":cat_id,
                                "innerData": []
                            }
                        categorized_expenses[category]["innerData"].append(item)
                    
                    result = list(categorized_expenses.values())

                elif type == "merchant":
                    categorized_expenses = {}
                    
                    for item in result:
                        category = item.get("cat")
                        merchant = item.get("merchant")
                        # cat_obj = Cat.objects(Q(label=category)).first()
                        # cat_id = str(cat_obj.id )if cat_obj else None
                        if merchant not in categorized_expenses:
                            categorized_expenses[merchant] = {
                                "headerName": merchant,
                                "cat_id":item.get("merchant_slug"),
                                "innerData": []
                            }
                        categorized_expenses[merchant]["innerData"].append(item)
                    result = list(categorized_expenses.values())

            except ValueError:
                # Handle case where index cannot be converted to an integer
                return {"error": "Invalid index value"}

        # Return result
        content = {
            "message": "All Data Fetched Successfully",
            "data": result,
        }
        return content

    
    @staticmethod
    async def graph_filter(request_data):
        time_type = request_data.get("time_type") 
        if time_type == "monthly":
            index = request_data.get("index") 
            result = []
            
        
            month = int(index) + 1
            current_year = datetime.now().year
            start_date = f"{current_year}-{month:02d}-01"
            _, last_day = monthrange(current_year, month)
            end_date = f"{current_year}-{month:02d}-{last_day:02d}"
            
            
            previous_month = int(index)
            previous_start_date = f"{current_year}-{previous_month:02d}-01"
            _, last_day = monthrange(current_year, previous_month)
            previous_end_date = f"{current_year}-{previous_month:02d}-{last_day:02d}"
            
            
            
            
            
            categories = Cat.objects()
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
                    & Q(date__gte=previous_start_date)
                    & Q(date__lte=previous_end_date)
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
            
            content = {
                "message": "All Data Fetched Successfully",
                "data": result,
            }
            return content
            
        elif time_type == "daily":
            date = request_data.get("index") 
            result = []

            categories = Cat.objects()
            specific_date = datetime.strptime(date, '%Y-%m-%d')
            previous_date = specific_date - timedelta(days=1)

            specific_date_str = specific_date.strftime('%Y-%m-%d')
            previous_date_str = previous_date.strftime('%Y-%m-%d')

            total_expense = 0
            previous_total_expense = 0

            for category in categories:
                label = category.label
                
                expenses = Expense.objects(Q(cat=label) & Q(date=specific_date_str))
                total_amount = sum(expense.amount for expense in expenses)
                total_expense += total_amount
                
                previous_day_expenses = Expense.objects(Q(cat=label) & Q(date=previous_date_str))
                previous_total_amount = sum(previous_day_expense.amount for previous_day_expense in previous_day_expenses)
                previous_total_expense += previous_total_amount
                
                result.append(
                    {
                        "category": label,
                        "amount": total_amount,
                        "previous_amount": previous_total_amount,
                    }
                )

        
                content = {
                    "message": "All Data Fetched Successfully",
                    "data": result,
                }
                return content
    
    
    
    
    
    
    
    #################################################################################################################
    @staticmethod
    async def graph_category(request_data):
        category_id = request_data.get('cat_id')
        today = datetime.now()
        start_date = today - timedelta(days=180)


        if category_id:
            cats = Cat.objects(id=category_id).only("label")
            cat_dict = {"label": cat.label for cat in cats}
            expenses = Expense.objects(cat=cat_dict.get('label'))
        else:
            expenses = Expense.objects()
            

        monthly_data = defaultdict(int)
        for i in range(6):
            month_num = (today.month - i - 1) % 12 + 1 
            monthly_data[month_num] = 0

        for expense in expenses:
            # Convert the string date to a datetime object
            if isinstance(expense.date, str):
                try:
                    expense_date = datetime.strptime(expense.date, "%Y-%m-%d")
                except ValueError:
                    print(f"Invalid date format for expense: {expense.date}")
                    continue
            else:
                expense_date = expense.date  # If already a datetime object

            # Only process expenses within the last 6 months
            if start_date <= expense_date <= today:
                month = expense_date.month
                monthly_data[month] += expense.amount  # Sum amounts for each month

        # Create the result list in the required format
        result = [{"month": str(month), "amount": str(amount)} for month, amount in sorted(monthly_data.items())]
        content = {
            "message": "All Data Fetched Successfully",
            "data": result,
        }
        return content