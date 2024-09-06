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
    cat: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, alias="start-date"),
    end_date: Optional[str] = Query(None, alias="end-date"),
    #  date: Optional[str] = Query(None)
):
   return await ExpenseController.cat_filter(cat, start_date, end_date)


@router.post("/cat/add")
async def add_cat( request: Request):
    return await ExpenseController.create_cat(request)


@router.post("/expense-gpt")
async def expense_gpt_message(request: Request):
    return await ExpenseController.expense_gpt(request)


