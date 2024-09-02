from fastapi.responses import JSONResponse # type: ignore
from fastapi import HTTPException,  APIRouter, Query, Request # type: ignore  
from ..services.alert_service import insert_alert, check_categories

async def set_alert(request):
    try:
        request_data = await request.json()
        check_cat = await check_categories(request_data.get('cat_ids'))
        if check_cat != len(request_data.get('cat_ids')):
            return JSONResponse(
                status_code=200,
                content={"message": "Please provide the categories properly"}
            )
        
        
        result = await insert_alert(request_data)
        response_data = {"status": "success", "result":request_data}
        return JSONResponse(
            status_code=200,
            content={"message": "Alert recorded successfully", "data": response_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))