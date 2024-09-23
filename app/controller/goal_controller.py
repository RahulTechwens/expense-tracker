from fastapi.responses import JSONResponse  # type: ignore
from fastapi import HTTPException # type: ignore
from ..services.goal_service import GoalsService
from ..helper.response_helper import ResponseServiceHelper 
from bson import ObjectId # type: ignore
from app.models.alert_model import Alert
from fastapi import HTTPException, APIRouter, Query, Request  # type: ignore


class GoalsController:
            
    async def add_goals(request: Request):
        try:
            request_data = await request.json()
            result = await GoalsService.add_goals(request_data)
            response_data = {"status": "success", "result": request_data}
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "Goal added successfully", "data": result}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
        
    async def delete_goals(goal_id):
        try:
            result = await GoalsService.delete_goals(goal_id)
            if result == True:
                return JSONResponse(
                    ResponseServiceHelper.success_helper(
                        200, 
                        {"message": "Goal deleted successfully", "data": result}
                    )
                )
            else:
                return JSONResponse(
                    ResponseServiceHelper.success_helper(
                        200, 
                        {"message": "Goal not found", "data": result}
                    )
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

            
    async def return_goals(goal_id):
        try:
            result = await GoalsService.all_goals(goal_id)
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "All goals fetched successfully", "data": result}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
    async def add_savings(request: Request):
        try:
            request_data = await request.json()
            result = await GoalsService.add_savings(request_data)
            response_data = {"status": "success", "result": request_data}
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "Savings amount added successfully", "data": result}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
    async def return_savings(goal_id):
        try:
            result = await GoalsService.return_savings(goal_id)
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "Savings entries fetched succesfully", "data": result}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def achieve_goals(goal_id, request):
        try:
            request_data = await request.json()
            result = await GoalsService.acheive(goal_id, request_data)
            return JSONResponse(
                ResponseServiceHelper.success_helper(
                    200, 
                    {"message": "Goal acheived successfully", "data": result}
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))