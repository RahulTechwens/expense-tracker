from app.models.expense_model import Expense
from fastapi import APIRouter, Request, Depends
from fastapi import FastAPI, HTTPException, Query, Request
# from fastapi import APIRouter, Query, Request, Depends, HTTPException # type: ignore
from typing import Optional
from app.controller.expense_controller import ExpenseController
from app.helper.otp_helper import OtpHelper


router = APIRouter()

# Dependency to check token
def verify_token(request: Request):
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    token = token.split(" ")[1] 
    check_token = OtpHelper.is_token_valid(token)
    return check_token



@router.get("/")
async def read_root():
    return {"Welcome message": "Welcome to the Expense Tracker API development server"}

@router.post("/expense/add")
async def expense_detail( request: Request, user = Depends(verify_token)):
    return await ExpenseController.create_expense(request, user)

@router.get("/expense")
async def filter_sms(
    request: Request,  # Add the request object to access the query string
    cat_id: Optional[str] = Query(None, alias="cat_id"),
    start_date: Optional[str] = Query(None, alias="start_date"),
    end_date: Optional[str] = Query(None, alias="end_date"),
    group_by: Optional[str] = Query(None, alias="group_by"),
    user = Depends(verify_token)
    
    #  date: Optional[str] = Query(None)
):
    return await ExpenseController.cat_filter(cat_id, start_date, end_date, group_by, user)

# @router.put("/expense/{}")

@router.post("/cat/add")
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
async def time_wise_expense(request: Request, user = Depends(verify_token)):
    return await ExpenseController.time_wise_expense(request, user)

@router.post("/graph")
async def graph_wise_expense(request: Request, user = Depends(verify_token)):
    return await ExpenseController.graph_wise_expense(request, user)

@router.post("/graph/categories")
async def graph_wise_categories(request: Request, user = Depends(verify_token)):
    return await ExpenseController.graph_wise_categories(request, user)

@router.put("/alter-cat")
async def alter_cat( request: Request, user = Depends(verify_token)):
    return await ExpenseController.alter_cat(request, user)