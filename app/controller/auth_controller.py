from fastapi.responses import JSONResponse
from fastapi import HTTPException
from app.helper.response_helper import ResponseServiceHelper
from app.services.auth_service import AuthService
class AuthController:
    async def login(request):
        try:
            request_data = await request.json()
            result = await AuthService.sign_up(request_data)
            return ResponseServiceHelper.success_helper(
                200,
                result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))