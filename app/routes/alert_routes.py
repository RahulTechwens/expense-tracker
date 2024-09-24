from fastapi import APIRouter, Request, Depends
from app.controller.alert_controller import AlertController
from fastapi import FastAPI, HTTPException, Query, Request
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from app.models.alert_model import ToggleStatusRequest
from app.helper.otp_helper import OtpHelper

router = APIRouter()

# Dependency to check token
def verify_token(request: Request):
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    token = token.split(" ")[1] 
    check_token = OtpHelper.is_token_valid(token)
    return check_token



@router.post("/set/alert")
async def set_alerts(request: Request,user: str = Depends(verify_token)):
    return await AlertController.set_alert(request, user)


@router.get("/alerts")
async def alerts(user: str = Depends(verify_token)):
    return await AlertController.get_alerts(user)




@router.put("/alerts/{alert_id}/change-status")
async def toggle_status(
    request: ToggleStatusRequest,
    alert_id: str = Path(..., description="The ID of the alert to update"),
    user: str = Depends(verify_token)
):
    status = request.active

    return await AlertController.toggle_status(alert_id, status, user)

@router.delete("/alerts")
async def delete_alerts(alert_ids:str = Query(...), user: str = Depends(verify_token)):
    return await AlertController.delete_alert(alert_ids, user)

@router.put("/alert/{alert_id}")
async def update_alert(alert_id: str, request: Request, user: str = Depends(verify_token)):
    return await AlertController.update_alert(alert_id, request, user)


