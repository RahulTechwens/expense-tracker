from fastapi import APIRouter, Request
from app.controller.auth_controller import AuthController

router = APIRouter()


@router.post('/login')
async def login(request: Request):
    return await AuthController.login(request)

@router.post('/verify/otp')
async def verify_otp(request: Request):
    return await AuthController.verify_otp(request)

@router.get('/verify')
async def verify_token(request: Request):
    return await AuthController.verify_token(request)

@router.post('/resend/otp')
async def login(request: Request):
    return await AuthController.resend_otp(request)