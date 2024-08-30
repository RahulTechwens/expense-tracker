from fastapi import HTTPException # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from app.models.expense_model import ExpenseRequest
from app.services.expense_service import insert_expense, filter_sms_category ,filter_sms_date_range,filter_sms_date, get_all_data

async def create_expense(expense_request: ExpenseRequest):
    
    #return cat, merchant, acct, bank,date, body, amount, type, method, manual, keywords, vector
    
    try:
        result = await insert_expense(expense_request)  # service call
        response_data = {"status": "success", "result":result}
        return JSONResponse(
            status_code=200,
            content={"message": "Expense recorded successfully", "data": response_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def cat_filter(cat):
    try:
        if cat:
            cat = cat.split(',')   
        else:
            cat = []     
        result = await filter_sms_category(cat)
        return JSONResponse(
            status_code=200,
            content={"Message": "Data Fetched Successfully", "Entered Categories":cat, "Filtered Data": result}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def date_range_filter(startDate:str, endDate:str):
    try:
        result = await filter_sms_date_range(startDate, endDate)
        return JSONResponse(
            status_code=200,
            content={"Message": "Data Fetched Successfully", "Entered Start Date":startDate,"Entered End Date":endDate, "Filtered Data": result}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def date_filter(date:str):
    try:
        result = await filter_sms_date(date)
        return JSONResponse(
            status_code=200,
            content={"Message": "Data Fetched Successfully", "Entered Date":date, "Filtered Data": result}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_all_data():
    try:
        result = await get_all_data()
        return JSONResponse(
            status_code=200,
            content={"Message": "All Data Fetched Successfully","Data": result}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        