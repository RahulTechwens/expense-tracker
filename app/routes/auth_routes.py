from fastapi import APIRouter, Request
from app.controller.auth_controller import AuthController

router = APIRouter()


@router.post('/login')
async def login(request: Request):
    return await AuthController.login(request)

