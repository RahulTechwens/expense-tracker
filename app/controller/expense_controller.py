from app.db.connection import mongodb
from app.models.expense_model import ExpenseRequest
from fastapi import HTTPException
from app.core.config import Settings
from pathlib import Path
from fastapi.responses import JSONResponse
from typing import List, Dict




async def entry_expense(amount: float, description: str) -> str:
    db = await mongodb.get_database()
    collection = db["expenses"] 

    document = {
        "amount": amount,
        "description": description,
    }
    
    # Insert into MongoDB
    insert_result = await collection.insert_one(document)
    
    return {"inserted_id": str(insert_result.inserted_id)}


# Define the upload directory
UPLOAD_DIR = Path(Settings.UPLOAD_DIR)

# Ensure the upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def upload_file(image: str) -> str:
# Define the file path 
    file_path = UPLOAD_DIR / image.filename

    # Save the image in upload file
    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    # Store the image path in MongoDB
    db = await mongodb.get_database()
    collection = db["images"]  # Use the "images" collection

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
    

#Fetch objects where cat are categories: List[str]
async def filter_sms_category (categories: List[str]):
    try:
        db = await mongodb.get_database()
        collection = db["demo_sms_data"] 
        
        # Filter
        cursor = collection.find({"cat": {"$in": categories}})
        data = await cursor.to_list(length=None) 
        
        # Convert to string
        for item in data:
            item["_id"] = str(item["_id"])
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# Fetch all objects from demo_sms_data and return
async def get_all_data ():
    try:
        db = await mongodb.get_database()
        collection = db["demo_sms_data"] 
        cursor = collection.find({})
        data = await cursor.to_list(length=None)
        
        # Convert to string
        for item in data:
            item["_id"] = str(item["_id"])
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

