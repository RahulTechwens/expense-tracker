from fastapi.responses import JSONResponse
from fastapi import HTTPException
from ..services.alert_service import AlertService
from ..helper.response_helper import ResponseServiceHelper 
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
            result = await AlertService().insert_alert(request_data)
            response_data = {"status": "success", "result": request_data}
            
            return JSONResponse(
                status_code=200,
                content={"message": "Alert recorded successfully", "data": response_data},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_alerts(user_id):
        try:
            print(user_id)
            result = await AlertService.all_alerts()
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "Fetch all the alerts", "data": result}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def toggle_status(alert_id: str, status:bool):
        try:
            response = await AlertService.toggle_alert_status(alert_id, status)
            if response:
                return JSONResponse(
                    ResponseServiceHelper.success_helper(
                        200, 
                        {"message": "Alert status updated", "data": {"alert_id":alert_id}}
                    )
                )
            else:
                return JSONResponse(
                    ResponseServiceHelper.success_helper(
                        404, 
                        {"message": "No such alert is present", "data": {"alert_id":alert_id}}
                    )
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def delete_alert(ids: list):
        try:
            splited_ids = ids.split(",")
            await AlertService.delete_alert(splited_ids)
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "Alert deleted successfully", "data": splited_ids}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update_alert(id: str, request):
        try:
            update_response = await AlertService.update_alert(id , request)
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "Alert updated successfully"}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        