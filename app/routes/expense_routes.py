# from app.db.connection import mongodb
from app.controller.expense_controller import create_expense, cat_filter, date_range_filter, date_filter
from app.models.expense_model import ExpenseRequest
from fastapi import APIRouter, Query # type: ignore
from typing import Optional

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Welcome message": "Welcome to the Expense Tracker API"}

@router.post("/expense/details")
async def expense_detail(expense_request: ExpenseRequest):
    return await create_expense(expense_request)


# @router.post("/upload")
# async def upload_image(image: UploadFile = File(...)):
#     return await upload_image_file(image)


#http://localhost:8000/api/filter/?cat=food
    
@router.get("/expense")
async def filter_sms(
    cat: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, alias="start-date"),
    end_date: Optional[str] = Query(None, alias="end-date"),
    date: Optional[str] = Query(None, alias="date"),
):
    if cat:
        return await cat_filter(cat)
    elif start_date and end_date:
        return await date_range_filter(start_date, end_date)
    elif date:
        return await date_filter(date)
    else:
        return {"message": "No valid filter parameter provided"}
