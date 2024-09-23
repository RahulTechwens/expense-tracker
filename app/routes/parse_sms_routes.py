from fastapi import APIRouter, Request  # type: ignore
from app.controller.parse_sms_controller import ParseSmsController
from fastapi import Request # type: ignore 
import re


router = APIRouter()


@router.post("/parse/sms")
async def parsing_message(request: Request):
    return await ParseSmsController().parsing_sms(request)


@router.get("/pasrse/sms/test")
async def parsing_message(request: Request):

    def generate_slug(merchant_name):
        merchant_name = merchant_name.lower()

        merchant_name = merchant_name.replace('&', 'and')
        
        merchant_name = re.sub(r'[\s\-]+', '_', merchant_name)
        
        merchant_slug = re.sub(r'[^\w_]', '', merchant_name)
        
        return merchant_slug

    # Example usage
    merchant = "Amazon F_resh"
    slug = generate_slug(merchant)
    print(slug)  # Output: h_and_m
    return slug



