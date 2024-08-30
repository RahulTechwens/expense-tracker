from fastapi import HTTPException # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from app.models.expense_model import ExpenseRequest
from app.services.expense_service import insert_expense, filter_sms_category

async def create_expense(expense_request: ExpenseRequest):
    amount = expense_request.amount
    description = expense_request.description
    try:
        result = await insert_expense(amount, description)  # service call
        response_data = {"status": "success", "result":result}
        return JSONResponse(
            status_code=200,
            content={"message": "Expense recorded successfully", "data": response_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def filter(cat):
    try:
        if cat:
            cat = cat.split(',')   
        else:
            cat = []     
        result = await filter_sms_category(cat)
        return JSONResponse(
            status_code=200,
            content={"message": "Data fetch successfully", "Entered Categories":cat, "Filtered Data": result}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
