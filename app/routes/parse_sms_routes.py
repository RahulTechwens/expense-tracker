from fastapi import APIRouter, Request  # type: ignore
from app.controller.parse_sms_controller import ParseSmsController
from fastapi import Request # type: ignore 

router = APIRouter()


@router.post("/pasrse/sms")
async def parsing_message(request: Request):
    return await ParseSmsController().parsing_sms(request)
