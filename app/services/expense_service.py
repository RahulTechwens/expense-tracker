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
                type=expense_request.get("type"),
                method=expense_request.get("method"),
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

            # If label exists in Predefined cat table or custom cat table, raise a validation error
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
    async def filter_sms_category(category_ids: List[str], start_date, end_date):
        # return [category_ids]
        # Fetch corresponding labels from the Cat collection
        cats = Cat.objects(id__in=category_ids).only("label")
        cat_dict = {str(cat.id): cat.label for cat in cats}
        
        #return cat_dict

        # Prepare a list of labels based on the category_ids
        categories = [cat_dict.get(cat_id, "Unknown") for cat_id in category_ids]
        #return categories

        query = Q()
        result = []


        if categories:
            query &= Q(cat__in=categories)
            # Fetch the data based on the constructed query
            data = Expense.objects(query)

            # If no data is found, return an empty list
            if data.count() == 0:
                return []

            # Convert the documents to a list of dictionaries
            for item in data:
                item_dict = item.to_mongo().to_dict()
                item_dict["_id"] = str(item_dict["_id"])
                result.append(item_dict)
        
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

        else:
            data = Expense.objects()

            for item in data:
                item_dict = item.to_mongo().to_dict()
                item_dict["_id"] = str(item_dict["_id"])
                result.append(item_dict)
                
                
        #Return result
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
