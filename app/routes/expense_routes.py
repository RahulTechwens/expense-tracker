from app.db.connection import mongodb
from app.controller.expense_controller import entry_expense, upload_file, filter_sms_category, get_all_data
from app.models.expense_model import ExpenseRequest
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from pathlib import Path
from app.core.config import Settings
import os
from typing import List, Dict



router = APIRouter()

@router.get("/")
async def read_root():
    return {"Welcom message": "Welcome to the Expense Tracker API"}

@router.post("/expense_detail")
async def expense_detail(expense_request: ExpenseRequest):
    amount = expense_request.amount
    description = expense_request.description

    try:
        result = await entry_expense(amount, description)
        return {"amount":amount, "description":description, "result": result, }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/upload_image")
async def upload_image(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image format")

    try:
        result = await upload_file(image)
        return {"result": result.body}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    


@router.get("/filter_sms_category/")
async def filter_sms(categories: List[str] = Query(...)):
    
    result = await filter_sms_category(categories)
    return {"Entered Categories":categories, "Filtered Data": result}




@router.get("/all_sms_data")
async def get_data():
    data = await get_all_data()
    return {"All Data": data}
    