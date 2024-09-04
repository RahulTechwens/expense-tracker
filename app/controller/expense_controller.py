from fastapi.responses import JSONResponse # type: ignore
from fastapi import HTTPException,  APIRouter, Query, Request # type: ignore
from app.services.expense_service import ExpenseService

class ExpenseController:
    async def create_expense(request: Request):
        try:
            request_data = await request.json()
            result = await ExpenseService.insert_expense(request_data)
            response_data = {"status": "success", "result":request_data}
            return JSONResponse(
                status_code=200,
                content={"message": "Expense recorded successfully", "data": response_data}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_cat(request: Request):
        try:
            request_data = await request.json()
            result = await ExpenseService.insert_cat(request_data)
            response_data = {"status": "success", "result":request_data}
            return JSONResponse(
                status_code=200,
                content={"message": "Expense recorded successfully", "data": response_data}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))    

    async def cat_filter(cat, start_date, end_date):
        try:
            cat = cat.split(',') if cat else []
            start_date = start_date or None
            end_date = end_date or None
            result = await ExpenseService.filter_sms_category(cat, start_date, end_date)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    
