# from fastapi import APIRouter, Request  # type: ignore
from app.controller.parse_sms_controller import ParseSmsController
from app.controller.parse_sms_controller_gemini import AIParseSmsController
from fastapi import Request # type: ignore 
import re
from fastapi import APIRouter, Request, Depends
from fastapi import FastAPI, HTTPException, Query, Request
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

@router.post("/parse/sms")
async def parsing_message(request: Request, user: str = Depends(verify_token)):
    return await ParseSmsController().parsing_sms(request, user)


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



# @router.post("/parse/sms")
# async def parsing_message(request: Request, user: str = Depends(verify_token)):
#     return await AIParseSmsController().sms_pasring(request, user)