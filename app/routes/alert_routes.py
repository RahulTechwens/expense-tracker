from fastapi import APIRouter, Request # type: ignore
from app.controller.alert_controller import AlertController

router = APIRouter()

@router.post("/set/alert")
async def set_alerts( request: Request):
    return await AlertController.set_alert(request)

@router.get("/alerts")
async def alerts():
   return await AlertController.get_alerts()