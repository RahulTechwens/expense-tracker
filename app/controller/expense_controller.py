# app/controllers/expense_controller.py

from app.db.connection import mongodb
from app.models.expense_model import ExpenseRequest
from fastapi import HTTPException


async def entry_expense(amount: float, description: str) -> str:
    db = await mongodb.get_database()
    collection = db["expenses"]  # Replace with your collection name
    
    # Prepare the document to be inserted
    document = {
        "amount": amount,
        "description": description,
    }
    
    # Insert the document into MongoDB
    insert_result = await collection.insert_one(document)
    
    return {"inserted_id": str(insert_result.inserted_id)}