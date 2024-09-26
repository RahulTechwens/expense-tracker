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
from dateutil.relativedelta import relativedelta

class ExpenseService:

    @staticmethod
    async def insert_expense(expense_request, user):
        print(user['phone'])
        def generate_slug(merchant_name):
            merchant_name = merchant_name.lower()
            merchant_name = re.sub(r"[\s\-]+", "_", merchant_name)
            merchant_slug = re.sub(r"[^\w_]", "", merchant_name)
            return merchant_slug

        def save_expense():
            merchant = expense_request.get("merchant")
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
                user_phone = user["phone"]
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
                        type="custom",  # type will always custom beacuse no predefined cat is allowed to add externally
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
        category_ids: List[str], start_date, end_date, group_by, user
    ):
        query = Q()
        if ObjectId.is_valid(category_ids[0]):  # will be resolving later
            cats = Cat.objects(id__in=category_ids).only("label")
            cat_dict = {str(cat.id): cat.label for cat in cats}
            categories = [cat_dict.get(cat_id, "Unknown") for cat_id in category_ids]
            query &= Q(cat__in=categories, user_phone=user['phone'])
        else:
            categories = category_ids
            query &= Q(merchant_slug__in=category_ids, user_phone=user['phone'])
        result = []
        print(categories, query)
        if categories:
            data = Expense.objects(query)
            if data.count() == 0:
                # return"yes"
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
                            "innerData": [],
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
                            "innerData": [],
                        }
                    grouped_by_merchant[merchant]["innerData"].append(item_dict)
                result = list(grouped_by_merchant.values())

            # Return result
            content = {
                "message": "All Data Fetched Successfully",
                "data": result,
            }
            return content

        else:
            data = Expense.objects()
            cat_color_codes = {cat.label: cat.color_code for cat in Cat.objects()}

            for item in data:
                item_dict = item.to_mongo().to_dict()
                item_dict["_id"] = str(item_dict["_id"])

                category = item_dict.get("cat")
                item_dict["color_code"] = cat_color_codes.get(category, "#ffffff")

                result.append(item_dict)

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
    async def time_wise_expense(request_data, user):
        time_type = request_data.get("time_type")
        index = request_data.get("index")
        type = request_data.get("type")
        query = Q()
        result = []

        if time_type == "daily":
            query &= Q(date=index, user_phone=user['phone'])

            if type == "category":
                categorized_expenses = {}

                # Fetch expenses matching the query (filtered by date)
                data = Expense.objects(query).order_by("-date")
                if data.count() == 0:
                    return []

                # Create a dictionary mapping category labels to color codes
                cat_color_codes = {cat.label: cat.color_code for cat in Cat.objects()}

                result = []
                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])

                    # Get the category
                    category = item_dict.get("cat")

                    if category not in categorized_expenses:
                        cat_obj = Cat.objects(Q(label=category)).first()
                        cat_id = str(cat_obj.id) if cat_obj else None
                        color_code = cat_color_codes.get(
                            category, "#ffffff"
                        )  # Default to white if no color is found

                        categorized_expenses[category] = {
                            "headerName": category,
                            "cat_id": cat_id,
                            "color_code": color_code,  # Add color code at the category level
                            "innerData": [],
                        }

                    # Append the item to the appropriate category
                    categorized_expenses[category]["innerData"].append(item_dict)

                # Convert the categorized dictionary to a list
                result = list(categorized_expenses.values())
                return result

            elif type == "merchant":
                categorized_expenses = {}
                data = Expense.objects(query).order_by("-date")
                if data.count() == 0:
                    return []

                # Step 1: Create a dictionary mapping category labels to color codes
                cat_color_codes = {cat.label: cat.color_code for cat in Cat.objects()}

                result = []
                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])

                    # Step 2: Get the category and append the color code
                    category = item_dict.get("cat")
                    item_dict["color_code"] = cat_color_codes.get(
                        category, "#ffffff"
                    )  # Default to white if no color found

                    result.append(item_dict)

                # Step 3: Build the categorized_expenses structure
                for item in result:
                    merchant = item.get("merchant")

                    if merchant not in categorized_expenses:
                        categorized_expenses[merchant] = {
                            "headerName": merchant,
                            "merchant_slug": item.get("merchant_slug"),
                            "innerData": [],
                        }

                    categorized_expenses[merchant]["innerData"].append(item)

                # Convert the dictionary to a list of categorized expenses
                result = list(categorized_expenses.values())

            elif type == "all":

                data = Expense.objects(query).order_by("-date")
                cat_color_codes = {cat.label: cat.color_code for cat in Cat.objects()}

                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])

                    category = item_dict.get("cat")

                    item_dict["color_code"] = cat_color_codes.get(category, "#ffffff")
                    result.append(item_dict)

        elif time_type == "monthly":
            try:
                month = int(index) + 1
                current_year = datetime.now().year
                start_date = f"{current_year}-{month:02d}-01"
                _, last_day = monthrange(current_year, month)
                end_date = f"{current_year}-{month:02d}-{last_day:02d}"
                query = Q(user_phone=user['phone']) &  Q(date__gte=start_date) &   Q(date__lte=end_date) 
                

                if type == "category":
                    data = Expense.objects(query).order_by("-date")

                    if data.count() == 0:
                        return []

                    categorized_expenses = {}

                    cat_color_codes = {
                        cat.label: cat.color_code for cat in Cat.objects()
                    }
                    
                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        item_dict["_id"] = str(item_dict["_id"])

                        category = item_dict.get("cat")
                        cat_obj = Cat.objects(Q(label=category)).first()
                        cat_id = str(cat_obj.id) if cat_obj else None
                        # print(cat_obj.label)
                        print(item_dict, end_date, start_date)
                        color_code = cat_color_codes.get(category, "#ffffff")

                        if category not in categorized_expenses:
                            categorized_expenses[category] = {
                                "headerName": category,
                                "cat_id": cat_id,
                                "color_code": color_code,
                                "innerData": [],
                            }

                        categorized_expenses[category]["innerData"].append(item_dict)

                    result = list(categorized_expenses.values())
                    return result

                elif type == "merchant":
                    categorized_expenses = {}
                    data = Expense.objects(query, user_phone=user['phone']).order_by("-date")

                    if data.count() == 0:
                        return []

                    cat_color_codes = {
                        cat.label: cat.color_code for cat in Cat.objects()
                    }

                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        item_dict["_id"] = str(item_dict["_id"])

                        category = item_dict.get("cat")
                        item_dict["color_code"] = cat_color_codes.get(
                            category, "#ffffff"
                        )

                        merchant = item_dict.get("merchant")

                        if merchant not in categorized_expenses:
                            categorized_expenses[merchant] = {
                                "headerName": merchant,
                                "merchant_slug": item_dict.get("merchant_slug"),
                                "innerData": [],
                            }

                        categorized_expenses[merchant]["innerData"].append(item_dict)

                    result = list(categorized_expenses.values())
                    return result

                elif type == "all":
                    # query = Q(user_phone=user['phone']) & Q(date__lte=end_date) &  Q(date__lte=end_date)
                    # data = Expense.objects(query)
                    data = Expense.objects(query).order_by("-date")

                    if data.count() == 0:
                        return []
                    # Create a dictionary mapping category labels to color codes
                    cat_color_codes = {
                        cat.label: cat.color_code for cat in Cat.objects()
                    }
                    result = []
                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        # Get the category and its corresponding color code
                        category = item_dict.get("cat")
                        item_dict["color_code"] = cat_color_codes.get(
                            category, "#ffffff"
                        )  # Default to white if no color is found

                        item_dict["_id"] = str(item_dict["_id"])
                        result.append(item_dict)

            except ValueError:
                return {"error": "Invalid index value"}

        # # Return result
        # content = {
        #     "message": "All Data Fetched Successfully",
        #     "data": result,
        # }
        return result

    # @staticmethod
    # async def time_wise_expense(request_data, user):
        time_type = request_data.get("time_type")
        index = request_data.get("index")
        type = request_data.get("type")
        query = Q()
        result = []

        if time_type == "daily":
            query &= Q(date=index, user_phone=user['phone'])

            if type == "category":
                categorized_expenses = {}

                # Fetch expenses matching the query (filtered by date)
                data = Expense.objects(query).order_by("-date")
                if data.count() == 0:
                    return []

                # Create a dictionary mapping category labels to color codes
                cat_color_codes = {cat.label: cat.color_code for cat in Cat.objects()}

                result = []
                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])

                    # Get the category
                    category = item_dict.get("cat")

                    if category not in categorized_expenses:
                        cat_obj = Cat.objects(Q(label=category)).first()
                        cat_id = str(cat_obj.id) if cat_obj else None
                        color_code = cat_color_codes.get(
                            category, "#ffffff"
                        )  # Default to white if no color is found

                        categorized_expenses[category] = {
                            "headerName": category,
                            "cat_id": cat_id,
                            "color_code": color_code,  # Add color code at the category level
                            "innerData": [],
                        }

                    # Append the item to the appropriate category
                    categorized_expenses[category]["innerData"].append(item_dict)

                # Convert the categorized dictionary to a list
                result = list(categorized_expenses.values())
                return result

            elif type == "merchant":
                categorized_expenses = {}
                data = Expense.objects(query).order_by("-date")
                if data.count() == 0:
                    return []

                # Step 1: Create a dictionary mapping category labels to color codes
                cat_color_codes = {cat.label: cat.color_code for cat in Cat.objects()}

                result = []
                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])

                    # Step 2: Get the category and append the color code
                    category = item_dict.get("cat")
                    item_dict["color_code"] = cat_color_codes.get(
                        category, "#ffffff"
                    )  # Default to white if no color found

                    result.append(item_dict)

                # Step 3: Build the categorized_expenses structure
                for item in result:
                    merchant = item.get("merchant")

                    if merchant not in categorized_expenses:
                        categorized_expenses[merchant] = {
                            "headerName": merchant,
                            "merchant_slug": item.get("merchant_slug"),
                            "innerData": [],
                        }

                    categorized_expenses[merchant]["innerData"].append(item)

                # Convert the dictionary to a list of categorized expenses
                result = list(categorized_expenses.values())

            elif type == "all":

                data = Expense.objects(query).order_by("-date")
                cat_color_codes = {cat.label: cat.color_code for cat in Cat.objects()}

                for item in data:
                    item_dict = item.to_mongo().to_dict()
                    item_dict["_id"] = str(item_dict["_id"])

                    category = item_dict.get("cat")

                    item_dict["color_code"] = cat_color_codes.get(category, "#ffffff")
                    result.append(item_dict)

        elif time_type == "monthly":
            try:
                month = int(index) + 1
                current_year = datetime.now().year
                start_date = f"{current_year}-{month:02d}-01"
                _, last_day = monthrange(current_year, month)
                end_date = f"{current_year}-{month:02d}-{last_day:02d}"
                query = Q(date__gte=start_date) & Q(date__lte=end_date)

                if type == "category":
                    data = Expense.objects(query, user_phone=user['phone']).order_by("-date")

                    if data.count() == 0:
                        return []

                    categorized_expenses = {}

                    cat_color_codes = {
                        cat.label: cat.color_code for cat in Cat.objects()
                    }

                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        item_dict["_id"] = str(item_dict["_id"])

                        category = item_dict.get("cat")
                        cat_obj = Cat.objects(Q(label=category)).first()
                        cat_id = str(cat_obj.id) if cat_obj else None

                        color_code = cat_color_codes.get(category, "#ffffff")

                        if category not in categorized_expenses:
                            categorized_expenses[category] = {
                                "headerName": category,
                                "cat_id": cat_id,
                                "color_code": color_code,
                                "innerData": [],
                            }

                        categorized_expenses[category]["innerData"].append(item_dict)

                    result = list(categorized_expenses.values())
                    return result

                elif type == "merchant":
                    categorized_expenses = {}
                    data = Expense.objects(query, user_phone=user['phone']).order_by("-date")

                    if data.count() == 0:
                        return []

                    cat_color_codes = {
                        cat.label: cat.color_code for cat in Cat.objects()
                    }

                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        item_dict["_id"] = str(item_dict["_id"])

                        category = item_dict.get("cat")
                        item_dict["color_code"] = cat_color_codes.get(
                            category, "#ffffff"
                        )

                        merchant = item_dict.get("merchant")

                        if merchant not in categorized_expenses:
                            categorized_expenses[merchant] = {
                                "headerName": merchant,
                                "merchant_slug": item_dict.get("merchant_slug"),
                                "innerData": [],
                            }

                        categorized_expenses[merchant]["innerData"].append(item_dict)

                    result = list(categorized_expenses.values())
                    return result

                elif type == "all":
                    query = Q(date__gte=start_date) & Q(date__lte=end_date)
                    # data = Expense.objects(query)
                    data = Expense.objects(query, user_phone=user['phone']).order_by("-date")

                    if data.count() == 0:
                        return []
                    # Create a dictionary mapping category labels to color codes
                    cat_color_codes = {
                        cat.label: cat.color_code for cat in Cat.objects()
                    }
                    result = []
                    for item in data:
                        item_dict = item.to_mongo().to_dict()
                        # Get the category and its corresponding color code
                        category = item_dict.get("cat")
                        item_dict["color_code"] = cat_color_codes.get(
                            category, "#ffffff"
                        )  # Default to white if no color is found

                        item_dict["_id"] = str(item_dict["_id"])
                        result.append(item_dict)

            except ValueError:
                return {"error": "Invalid index value"}

        # # Return result
        # content = {
        #     "message": "All Data Fetched Successfully",
        #     "data": result,
        # }
        return result

    # @staticmethod
    # async def graph_filter(request_data, user):
    #     time_type = request_data.get("time_type")
    #     if time_type == "monthly":
    #         index = request_data.get("index")
    #         result = []

    #         month = int(index) + 1
    #         current_year = datetime.now().year

    #         # Calculate start and end dates for the current month
    #         start_date = f"{current_year}-{month:02d}-01"
    #         _, last_day = monthrange(current_year, month)
    #         end_date = f"{current_year}-{month:02d}-{last_day:02d}"

    #         # Calculate start and end dates for the previous month
    #         previous_month = int(index)
    #         previous_start_date = f"{current_year}-{previous_month:02d}-01"
    #         _, last_day = monthrange(current_year, previous_month)
    #         previous_end_date = f"{current_year}-{previous_month:02d}-{last_day:02d}"

    #         total_expense = 0.0
    #         previous_total_expense = 0.0

    #         expenses = Expense.objects(
    #             Q(date__gte=start_date) & Q(date__lte=end_date) & Q(user_phone=user['phone'])
    #         ).order_by("-date")

    #         latest_categories = []
    #         seen_categories = set()

    #         for expense in expenses:
    #             if expense.cat not in seen_categories:
    #                 seen_categories.add(expense.cat)
    #                 latest_categories.append(expense.cat)
    #             if len(latest_categories) >= 6:
    #                 break

    #         # return latest_categories


    #         for category in latest_categories:

    #             expenses = Expense.objects(
    #                 Q(cat=category, user_phone=user['phone']) & Q(date__gte=start_date) & Q(date__lte=end_date)
    #             )

    #             total_amount = sum(float(expense.amount) for expense in expenses)
    #             total_expense += total_amount

    #             previous_day_expenses = Expense.objects(
    #                 Q(cat=category)
    #                 & Q(date__gte=previous_start_date)
    #                 & Q(date__lte=previous_end_date)
    #             )
    #             previous_total_amount = sum(
    #                 float(previous_day_expense.amount)
    #                 for previous_day_expense in previous_day_expenses
    #             )
    #             previous_total_expense += previous_total_amount

    #             result.append(
    #                 {
    #                     "category": category,
    #                     "amount": round(float(total_amount), 2),
    #                     "previous_amount": round(float(previous_total_amount), 2),
    #                 }
    #             )

    #         content = {
    #             "message": "All Data Fetched Successfully",
    #             "data": result,
    #         }
    #         return content

    #     elif time_type == "daily":
    #         date = request_data.get("index")
    #         result = []

    #         # categories = Cat.objects()
    #         specific_date = datetime.strptime(date, "%Y-%m-%d")

    #         specific_date_start = specific_date.strftime("%Y-%m-%d")
    #         specific_date_end = specific_date.strftime("%Y-%m-%d")

    #         previous_date = specific_date - timedelta(days=1)

    #         previous_date_start = previous_date.strftime("%Y-%m-%d")
    #         previous_date_end = previous_date.strftime("%Y-%m-%d")

    #         total_expense = 0.0
    #         previous_total_expense = 0.0


    #         expenses = Expense.objects(
    #             Q(date__gte=specific_date_start) & Q(date__lte=specific_date_end)  & Q(date__lte=end_date)
    #         ).order_by("-date")

    #         latest_categories = []
    #         seen_categories = set()

    #         for expense in expenses:
    #             if expense.cat not in seen_categories:
    #                 seen_categories.add(expense.cat)
    #                 latest_categories.append(expense.cat)
    #             if len(latest_categories) >= 6:
    #                 break

    #         # return latest_categories

    #         for category in latest_categories:
    #             # label = category.label

    #             expenses = Expense.objects(
    #                 Q(cat=category) & Q(date__gte=specific_date_start) & Q(date__lte=specific_date_end)  & Q(date__lte=end_date)
    #             )
    #             total_amount = sum(float(expense.amount) for expense in expenses)
    #             total_expense += total_amount

    #             previous_day_expenses = Expense.objects(
    #                 Q(cat=category)  & Q(date__lte=end_date)
    #                 & Q(date__gte=previous_date_start)
    #                 & Q(date__lte=previous_date_end)
    #             )
    #             previous_total_amount = sum(
    #                 float(previous_day_expense.amount)
    #                 for previous_day_expense in previous_day_expenses
    #             )  # Cast to float
    #             previous_total_expense += previous_total_amount

    #             result.append(
    #                 {
    #                     "category": category,
    #                     "amount": round(float(total_amount), 2),
    #                     "previous_amount": round(float(previous_total_amount), 2),
    #                 }
    #             )
    #         content = {
    #             "message": "All Data Fetched Successfully",
    #             "data": result,
    #         }
    #         return content
        
        
    # @staticmethod
    # async def graph_filter(request_data, user):
    #     time_type = request_data.get("time_type")
    #     if time_type == "monthly":
    #         index = request_data.get("index")
    #         result = []

    #         month = int(index) + 1
    #         current_year = datetime.now().year

    #         # Calculate start and end dates for the current month
    #         start_date = f"{current_year}-{month:02d}-01"
    #         _, last_day = monthrange(current_year, month)
    #         end_date = f"{current_year}-{month:02d}-{last_day:02d}"

    #         # Calculate start and end dates for the previous month
    #         previous_month = int(index)
    #         previous_start_date = f"{current_year}-{previous_month:02d}-01"
    #         _, last_day = monthrange(current_year, previous_month)
    #         previous_end_date = f"{current_year}-{previous_month:02d}-{last_day:02d}"

    #         categories = Cat.objects()
    #         total_expense = 0.0
    #         previous_total_expense = 0.0
    #         # expenses = Expense.objects(
    #         #     Q(date__gte=start_date) & Q(date__lte=end_date)
    #         # ).order_by("-date")
    #         # return expenses.to_json()
    #         # Get distinct categories (unique) sorted by the latest date, and limit the result to 6
    #         # latest_categories = expenses.distinct("cat")[:6]
    #         #return start_date
    #         # Print or use the latest unique categories
    #         # return latest_categories

    #         for category in categories:
    #             # label = category.label

    #             expenses = Expense.objects(
    #                 Q(cat=category) & Q(date__gte=start_date) & Q(date__lte=end_date) & Q(user_phone=user['phone'])
    #             )

    #             total_amount = sum(float(expense.amount) for expense in expenses)
    #             total_expense += total_amount

    #             previous_day_expenses = Expense.objects(
    #                 Q(cat=category)
    #                 & Q(user_phone=user['phone'])
    #                 & Q(date__gte=previous_start_date)
    #                 & Q(date__lte=previous_end_date)
    #             )
    #             previous_total_amount = sum(
    #                 float(previous_day_expense.amount)
    #                 for previous_day_expense in previous_day_expenses
    #             )
    #             previous_total_expense += previous_total_amount

    #             result.append(
    #                 {
    #                     "category": category,
    #                     "amount": round(float(total_amount), 2),
    #                     "previous_amount": round(float(previous_total_amount), 2),
    #                 }
    #             )

    #         content = {
    #             "message": "All Data Fetched Successfully",
    #             "data": result,
    #         }
    #         return content

    #     elif time_type == "daily":
    #         date = request_data.get("index")
    #         result = []

    #         categories = Cat.objects()
    #         specific_date = datetime.strptime(date, "%Y-%m-%d")
    #         previous_date = specific_date - timedelta(days=1)

    #         specific_date_str = specific_date.strftime("%Y-%m-%d")
    #         previous_date_str = previous_date.strftime("%Y-%m-%d")

    #         total_expense = 0.0
    #         previous_total_expense = 0.0

    #         for category in categories:
    #             label = category.label

    #             expenses = Expense.objects(Q(cat=label) & Q(date=specific_date_str))
    #             total_amount = sum(float(expense.amount) for expense in expenses)
    #             total_expense += total_amount

    #             previous_day_expenses = Expense.objects(
    #                 Q(cat=label) & Q(date=previous_date_str) & Q(user_phone=user['phone'])
    #             )
    #             previous_total_amount = sum(
    #                 float(previous_day_expense.amount)
    #                 for previous_day_expense in previous_day_expenses
    #             )  # Cast to float
    #             previous_total_expense += previous_total_amount

    #             result.append(
    #                 {
    #                     "category": label,
    #                     "amount": round(float(total_amount), 2),
    #                     "previous_amount": round(float(previous_total_amount), 2),
    #                 }
    #             )
    #         content = {
    #             "message": "All Data Fetched Successfully",
    #             "data": result,
    #         }
    #         return content
        
        
    
    @staticmethod
    async def graph_filter(request_data, user):
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
            total_expense = 0.0 
            previous_total_expense = 0.0  

            for category in categories:
                label = category.label
                
                # print(label)
                
                expenses = Expense.objects(
                    Q(cat=label, user_phone=user['phone']) & Q(date__gte=start_date) & Q(date__lte=end_date) 
                )
                for item in expenses:
                    print(item.cat)
                total_amount = sum(float(expense.amount) for expense in expenses)
                total_expense += total_amount
                
                previous_day_expenses = Expense.objects(
                    Q(cat=label,  user_phone=user['phone']) & Q(date__gte=previous_start_date) & Q(date__lte=previous_end_date)
                )
                previous_total_amount = sum(
                    float(previous_day_expense.amount) for previous_day_expense in previous_day_expenses
                )
                previous_total_expense += previous_total_amount
                
                if total_amount > 0:
                    result.append(
                        {
                            "category": label,
                            "amount": round(float(total_amount), 2),
                            "previous_amount": round(float(previous_total_amount), 2),
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
            specific_date = datetime.strptime(date, "%Y-%m-%d")
            previous_date = specific_date - timedelta(days=1)

            specific_date_str = specific_date.strftime("%Y-%m-%d")
            previous_date_str = previous_date.strftime("%Y-%m-%d")

            total_expense = 0.0
            previous_total_expense = 0.0

            for category in categories:
                label = category.label

                expenses = Expense.objects(Q(cat=label) & Q(date=specific_date_str) & Q( user_phone=user['phone']))
                total_amount = sum(float(expense.amount) for expense in expenses)
                total_expense += total_amount

                previous_day_expenses = Expense.objects(Q(cat=label) & Q(date=previous_date_str) & Q( user_phone=user['phone']))
                previous_total_amount = sum(float(previous_day_expense.amount) for previous_day_expense in previous_day_expenses)  # Cast to float
                previous_total_expense += previous_total_amount

                
                if total_amount > 0:
                    result.append(
                        {
                            "category": label,
                            "amount": round(float(total_amount), 2),
                            "previous_amount": round(float(previous_total_amount), 2),
                        }
                    )
            content = {
                "message": "All Data Fetched Successfully",
                "data": result,
            }
            return content
        

    @staticmethod
    async def graph_category(request_data, user):
        category_id = request_data.get("cat_id")
        query = Q()
        if ObjectId.is_valid(category_id):
            cats = Cat.objects(id=category_id).only("label")
            cat_dict = {"label": cat.label for cat in cats}
            query &= Q(cat=cat_dict.get("label"), user_phone=user['phone'])
        else:
            query &= Q(merchant_slug=category_id, user_phone=user['phone'])

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
        result = [
            {"month": str(month), "amount": str(amount)}
            for month, amount in sorted(monthly_data.items())
        ]
        content = {
            "message": "All Data Fetched Successfully",
            "data": result,
        }
        return content

    @staticmethod
    async def alter_cat(alter_request, user):
        expense_id = alter_request.get("expense_id")
        new_cat_id = alter_request.get("new_cat_id")

        expense = Expense.objects(id=expense_id, user_phone=user['phone']).first()
        new_cat = Cat.objects(id=new_cat_id).first()
        new_cat_name = new_cat.label

        if expense:
            expense.cat = new_cat_name
            expense.save()
        return {"message": "category updated"}



    @staticmethod
    def _group_by_period(expenses, period_type, start_date, end_date):
        grouped_data = defaultdict(float)
        
        for expense in expenses:
            expense_date = datetime.strptime(expense.date, '%Y-%m-%d')
            
            if period_type == "day":
                period = expense_date.strftime('%Y-%m-%d')
            elif period_type == "month":
                period = int(expense_date.strftime('%m')) - 1
            elif period_type == "year":
                period = expense_date.strftime('%Y')
            
            grouped_data[period] += expense.amount
        
        periods = []
        current_date = start_date

        if period_type == "day":
            while current_date <= end_date:
                periods.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
        elif period_type == "month":
            while current_date <= end_date:
                periods.append(current_date.month - 1)
                current_date += relativedelta(months=1)
        elif period_type == "year":
            while current_date <= end_date:
                periods.append(current_date.strftime('%Y'))
                current_date += relativedelta(years=1)
        
        response = [{"month" if period_type == "month" else period_type: str(period), "amount": float(grouped_data.get(period, 0))} for period in periods]
        
        return response

    @staticmethod
    async def graph(type, user):
        filter_type = type
        today = datetime.now().date()
        response = []

        if filter_type == 'daily':
            six_days_ago = today - timedelta(days=6)
            expenses = Expense.objects(Q(date__gte=str(six_days_ago)) & Q(date__lte=str(today)) & Q(user_phone=user['phone']))
            response = ExpenseService._group_by_period(expenses, "day", six_days_ago, today)
        
        elif filter_type == 'monthly':
            six_months_ago = today - relativedelta(months=6)
            expenses = Expense.objects(Q(date__gte=str(six_months_ago)) & Q(date__lte=str(today)) & Q(user_phone=user['phone']))
            response = ExpenseService._group_by_period(expenses, "month", six_months_ago, today)
        
        elif filter_type == 'yearly':
            six_years_ago = today - relativedelta(years=6)
            expenses = Expense.objects(Q(date__gte=str(six_years_ago)) & Q(date__lte=str(today)) & Q(user_phone=user['phone']))
            response = ExpenseService._group_by_period(expenses, "year", six_years_ago, today)
        
        else:
            return []
        
        return {
            "message": "Graph Fetched Successfully",
            "data": response,
        }

