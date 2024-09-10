from app.db.connection import mongodb
from app.models.expense_model import Expense, Cat, Message
from typing import List
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from concurrent.futures import ThreadPoolExecutor
import asyncio

class ExpenseService:

    @staticmethod
    async def insert_expense(expense_request):
        try:
            def save_expense():
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
                return str(expense.id)

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                inserted_id = await loop.run_in_executor(pool, save_expense)
            
            return {"inserted_id": inserted_id}

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @staticmethod
    async def insert_cat(expense_request):
        try:
            def save_cat():
                cat = Cat(
                    icon_id=expense_request.get('icon_id'),
                    label=expense_request.get('label'),
                )
                cat.save()
                return str(cat.id)

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                inserted_id = await loop.run_in_executor(pool, save_cat)
            
            return {"inserted_id": inserted_id}

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @staticmethod
    async def filter_sms_category(categories: List[str], start_date, end_date):
        query = Q()

        if categories:
            query &= Q(cat__in=categories)
            # Fetch the data based on the constructed query
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
                content={
                    "Message": "Data Fetched Successfully",
                    "Entered_Categories": categories,
                    "Filtered_Data": result,
                },
            )
        # http://127.0.0.1:8000/api/expense?start-date=2024-09-02T00:00:00&end-date=2024-09-02T23:59:59
        elif start_date and end_date:

            categories = Cat.objects()

            # prevous day starting and ending
            start_datetime = datetime.fromisoformat(start_date)
            starting_datetime = start_datetime - timedelta(days=1)
            previous_day_start_date = starting_datetime.isoformat()

            end_datetime = datetime.fromisoformat(end_date)
            ending_datetime = end_datetime - timedelta(days=1)
            previous_day_end_date = ending_datetime.isoformat()

            # Initialize a list to store the label and amount pairs
            result = []
            total_expense = 0
            previous_total_expense = 0
            # calculate the sum of amounts for each label within the time span
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

                # Add the label and amount to the result list
                result.append(
                    {
                        "category": label,
                        "amount": total_amount,
                        "previous_amount": previous_total_amount,
                    }
                )

            return JSONResponse(
                status_code=200,
                content={
                    "Message": "Data of The Day and Previous Day Fetched Successfully",
                    "Data":             [
                    {
                        "Current_day": f"{start_date} to {end_date}",
                        "Current_day_total_expense": total_expense,
                        "Previous_day": f"{previous_day_start_date} to {previous_day_end_date}",
                        "Previous_day_total_expense": previous_total_expense,
                        "Summary": result,
                    },
                ],
                },
            )
        else:
            data = Expense.objects()
            result = []
            for item in data:
                item_dict = item.to_mongo().to_dict()
                item_dict["_id"] = str(item_dict["_id"])
                result.append(item_dict)

            return JSONResponse(
                status_code=200,
                content={
                    "Message": "All Data Fetched Successfully",
                    "Filtered_Data": result,
                },
            )
        
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

        return JSONResponse(
            status_code=200,
            content={
                "Message": "All Category Fetched Successfully",
                "Filtered_Data": result,
            },
        )
        
