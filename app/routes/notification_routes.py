from fastapi import APIRouter, Request, Depends
from app.controller.notification_controller import NotificationController

router = APIRouter()


@router.post("/send/notification")
async def send_notification(request: Request):
    return await NotificationController.send_notification(request)