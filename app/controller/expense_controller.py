from app.db.connection import mongodb
from app.models.expense_model import ExpenseRequest
from fastapi import HTTPException


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