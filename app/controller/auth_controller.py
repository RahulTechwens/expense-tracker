from fastapi.responses import JSONResponse
from fastapi import HTTPException
from app.helper.response_helper import ResponseServiceHelper
from app.services.auth_service import AuthService
class AuthController:
    async def login(request):
        try:
            request_data = await request.json()
            result = await AuthService.send(request_data)
            return ResponseServiceHelper.success_helper(
                200,
                result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def verify_otp(request):
        try:
            request_data = await request.json()
            result = await AuthService.verify(request_data)
            
            if result['status']:
                return ResponseServiceHelper.success_helper(
                    200,
                    result
                )
            else:
                return ResponseServiceHelper.success_helper(
                    400,
                    result
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Verify Token
    async def verify_token(request):
        try:
            request_header =  request.headers.get('authorization')
            token = request_header.split(" ")[1]
            result = await AuthService.verify_token(token)
            return ResponseServiceHelper.success_helper(
                200,
                result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    # Resend OTP   
    async def resend_otp(request):
        try:
            request_data = await request.json()
            result = await AuthService.resend_otp(request_data)
            return ResponseServiceHelper.success_helper(
                200,
                result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))