from fastapi.responses import JSONResponse  # type: ignore
from fastapi import HTTPException # type: ignore
from ..services.alert_service import AlertService
from ..helper.response_helper import ResponseServiceHelper 
from app.db.connection import mongodb
        
from fastapi import HTTPException

from bson import ObjectId
from app.models.alert_model import Alert

class AlertController:
    async def set_alert(request):
        try:
            request_data = await request.json()
            check_cat = await AlertService.check_categories(request_data.get("cat_ids"))
            if check_cat != len(request_data.get("cat_ids")):
                return JSONResponse(
                    status_code=200,
                    content={"message": "Please provide the categories properly"},
                
                )
            result = await AlertService.insert_alert(request_data)
            response_data = {"status": "success", "result": request_data}
            
            return JSONResponse(
                status_code=200,
                content={"message": "Alert recorded successfully", "data": response_data},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_alerts():
        try:
            result = await AlertService.all_alerts()
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "Expense recorded successfully", "data": result}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        


    async def toggle_status(alert_id: str, status:bool):
        try:
            response = await AlertService.toggle_alert_status(alert_id, status)
            return response
        except HTTPException as e:
            raise e