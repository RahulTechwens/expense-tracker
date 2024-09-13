from app.models.expense_model import Expense
from fastapi import APIRouter, Query, Request # type: ignore
from typing import Optional
from app.controller.expense_controller import ExpenseController

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Welcome message": "Welcome to the Expense Tracker API"}

@router.post("/expense/add")
async def expense_detail( request: Request):
    return await ExpenseController.create_expense(request)

@router.get("/expense")
async def filter_sms(
    request: Request,  # Add the request object to access the query string
    cat_id: Optional[str] = Query(None, alias="cat-_id"),
    start_date: Optional[str] = Query(None, alias="start_date"),
    end_date: Optional[str] = Query(None, alias="end_date"),
    group_by: Optional[str] = Query(None, alias="group_by"),
    
    #  date: Optional[str] = Query(None)
):
    return await ExpenseController.cat_filter(cat_id, start_date, end_date, group_by)

# @router.put("/expense/{}")

@router.post("/custom-cat/add")
async def add_cat( request: Request):
    return await ExpenseController.create_custom_cat(request)

@router.put("/rename-custom-cat")
async def rename_cat( request: Request):
    return await ExpenseController.rename_custom_cat(request)

@router.get("/cat")
async def all_cat():
    return await ExpenseController.all_cat()

@router.post("/expense-gpt")
async def expense_gpt_message(request: Request):
    return await ExpenseController.expense_gpt(request)

@router.post("/expense/get")
async def time_wise_expense(request: Request):
    return await ExpenseController.time_wise_expense(request)




