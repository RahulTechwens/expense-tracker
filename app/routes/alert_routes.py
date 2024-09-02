from app.models.expense_model import Expense
from fastapi import APIRouter, Query, Request # type: ignore
from typing import Optional
from app.controller.alert_controller import set_alert

router = APIRouter()

@router.post("/set/alert")
async def set_alerts( request: Request):
    return await set_alert(request)