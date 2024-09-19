from app.db.connection import mongodb
from app.models.expense_model import Expense, Cat, Message
from typing import List
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q  # type: ignore
from mongoengine import ValidationError
from fastapi.responses import JSONResponse  # type: ignore
from concurrent.futures import ThreadPoolExecutor
from mongoengine import DoesNotExist
import asyncio, re
from collections import defaultdict
from calendar import monthrange
from mongoengine.queryset.visitor import Q
from bson.objectid import ObjectId


class ExpenseService:

    @staticmethod
    async def insert_expense(expense_request):
        def generate_slug(merchant_name):
            merchant_name = merchant_name.lower()
            merchant_name = re.sub(r'[\s\-]+', '_', merchant_name)
            merchant_slug = re.sub(r'[^\w_]', '', merchant_name)
            return merchant_slug
        
        def save_expense():
            merchant=expense_request.get("merchant")
            merchant_slug = generate_slug(merchant)
            expense = Expense(
                cat=expense_request.get("cat"),
                merchant=expense_request.get("merchant"),
                merchant_slug=merchant_slug,
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
            # is_parent = Cat.objects.get(id=parent_genre_id)
            label = expense_request.get("label")
            existing_cat = Cat.objects(label=label).first()
            # existing_custom_cat = Cat.objects(label=label).first()
            
            if existing_cat:
                raise ValidationError(f"The label '{label}' already exists.")
            else:

                def save_cat():
                    cat = Cat(
                        icon_id=expense_request.get("icon_id"),
                        label=expense_request.get("label"),
                        type=expense_request.get("type"),
                        color_code=expense_request.get("color_code"),
                        # parent_genre_id=expense_request.get("parent_genre_id"),
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
        query = Q()
        if ObjectId.is_valid(category_ids[0]): # will be resolving later
            cats = Cat.objects(id__in=category_ids).only("label")
            cat_dict = {str(cat.id): cat.label for cat in cats}
            categories = [cat_dict.get(cat_id, "Unknown") for cat_id in category_ids]
            query &= Q(cat__in=categories)
        else:
            categories=category_ids
            query &= Q(merchant_slug__in=category_ids)
        result = []
        print(categories, query)
        if categories:
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

    # Check custom or predefined 
    @staticmethod
    async def rename_custom_cat(rename_request):
        id = rename_request.get("id")
        new_label = rename_request.get("new_label")
        cat = Cat.objects(id=id).first()
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


                if type == "category":
                    # query = Q(date__gte=start_date) & Q(date__lte=end_date)
                    data = Expense.objects(query)

                    if data.count() == 0:
                        return []

                    result = []
                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        item_dict["_id"] = str(item_dict["_id"])
                        result.append(item_dict)
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
                    # query = Q(date__gte=start_date) & Q(date__lte=end_date)
                    data = Expense.objects(query)

                    if data.count() == 0:
                        return []

                    result = []
                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        item_dict["_id"] = str(item_dict["_id"])
                        result.append(item_dict)
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
                
                elif type == "all":
                    query = Q(date__gte=start_date) & Q(date__lte=end_date)
                    # data = Expense.objects(query)
                    data = Expense.objects(query).order_by('-date')

                    if data.count() == 0:
                        return []

                    result = []
                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        item_dict["_id"] = str(item_dict["_id"])
                        result.append(item_dict)
                     
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
        query = Q()
        if ObjectId.is_valid(category_id):
            cats = Cat.objects(id=category_id).only("label")
            cat_dict = {"label": cat.label for cat in cats}
            query &= Q(cat=cat_dict.get('label'))
        else:
            query &= Q(merchant_slug=category_id)
            
        today = datetime.now()
        start_date = today - timedelta(days=180)


        if category_id:
           
            expenses = Expense.objects(query)
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
    
    
    @staticmethod
    async def alter_cat(alter_request):
        expense_id = alter_request.get("expense_id")
        new_cat_id = alter_request.get("new_cat_id")
        
        expense = Expense.objects(id=expense_id).first()
        new_cat = Cat.objects(id=new_cat_id).first()
        new_cat_name = new_cat.label
        
        if expense:
            expense.cat = new_cat_name
            expense.save()
        return {"message":"categories updated"}
    