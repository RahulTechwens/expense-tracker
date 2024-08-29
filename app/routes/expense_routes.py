from app.db.connection import mongodb
from app.controller.expense_controller import entry_expense
from app.models.expense_model import ExpenseRequest
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from app.core.config import Settings
import os


router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Welcome to the Expense Tracker API"}

@router.post("/expense_detail")
async def expense_detail(expense_request: ExpenseRequest):
    amount = expense_request.amount
    description = expense_request.description

    try:
        result = await entry_expense(amount, description)
        return {"amount":amount, "description":description, "result": result, }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# app/controllers/image_upload.py


# Define the upload directory inside 'app'
UPLOAD_DIR = Path(Settings.UPLOAD_DIR)

# Ensure the upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload_image")
async def upload_image(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image format")

    # Define the file path in the 'app/upload' directory
    file_path = UPLOAD_DIR / image.filename

    # Save the image to the file system
    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    # Store the image path and other metadata in MongoDB
    db = await mongodb.get_database()
    collection = db["images"]  # Use the "images" collection

    # Prepend the base URL to the file path
    base_url = "http://127.0.0.1:8000/"
    document = {
        "image_filename": image.filename,
        "file_path": base_url + str(file_path.relative_to("app")),
        "content_type": image.content_type
    }

    insert_result = await collection.insert_one(document)

    return JSONResponse(
        status_code=200,
        content={
            "filename": image.filename,
            "filepath": base_url + str(file_path.relative_to("app")),
            "inserted_id": str(insert_result.inserted_id)
        }
    )
