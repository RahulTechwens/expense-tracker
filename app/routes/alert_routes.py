from fastapi import APIRouter, Request  # type: ignore
from app.controller.alert_controller import AlertController
from fastapi import FastAPI, HTTPException, Query, Request
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from app.models.alert_model import ToggleStatusRequest

router = APIRouter()


@router.post("/set/alert")
async def set_alerts(request: Request):
    return await AlertController.set_alert(request)


@router.get("/alerts")
async def alerts():
    return await AlertController.get_alerts()


@router.put("/alerts/{alert_id}/change-status")
async def toggle_status(
    request: ToggleStatusRequest,
    alert_id: str = Path(..., description="The ID of the alert to update"),
):
    status = request.active

    return await AlertController.toggle_status(alert_id, status)

@router.delete("/alerts")

async def delete_alerts(alert_ids:str = Query(...)):
    return await AlertController.delete_alert(alert_ids)