from app.db.connection import mongodb
from app.models.expense_model import Expense, Cat
from typing import List, Dict
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q # type: ignore


async def insert_expense(expense_request):
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
    return {"inserted_id": str(expense.id)}


async def insert_cat(expense_request):
    cat = Cat(
        icon_id=expense_request.get('icon_id'),
        label=expense_request.get('label'),
    )
    cat.save()
    return {"inserted_id": str(cat.id)}


async def filter_sms_category (categories: List[str], start_date, end_date):
    query = Q()
    if categories:
        query &= Q(cat__in=categories)
    if start_date and start_date:
        query &= Q(date__gte=start_date, date__lte=end_date)
    elif start_date:
        query &= Q(date__gte=start_date)
    elif end_date:
        query &= Q(date__lte=end_date)
    data = Expense.objects(query)
    if data.count() == 0:
        return []
    result = []
    for item in data:
        item_dict = item.to_mongo().to_dict()
        item_dict["_id"] = str(item_dict["_id"])
        result.append(item_dict)
    
    return result
        