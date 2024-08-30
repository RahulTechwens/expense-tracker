# from app.db.connection import mongodb
from app.controller.expense_controller import create_expense, filter
from app.models.expense_model import ExpenseRequest
from fastapi import APIRouter, Query # type: ignore

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Welcom message": "Welcome to the Expense Tracker API"}

@router.post("/expense/details")
async def expense_detail(expense_request: ExpenseRequest):
    return await create_expense(expense_request)


# @router.post("/upload")
# async def upload_image(image: UploadFile = File(...)):
#     return await upload_image_file(image)

@router.get("/filter")
async def filter_sms(cat: str = Query(None)):
    return await filter(cat)
