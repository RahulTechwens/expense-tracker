from app.models.expense_model import Expense
from fastapi import APIRouter, Query, Request, HTTPException, Depends # type: ignore
from typing import Optional
from app.controller.goal_controller import GoalsController
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



@router.get("/goals")
async def return_goals(
    request: Request,
    goal_id: Optional[str] = Query(None, alias="goal_id"),
    user: str = Depends(verify_token)
):
    return await GoalsController.return_goals(goal_id, user)

@router.post("/goals/add")
async def add_goals(request: Request, user: str = Depends(verify_token)):
    return await GoalsController.add_goals(request, user)

@router.delete("/goals/delete")
async def delete_goals(goal_id:str = Query(...), user: str = Depends(verify_token)):
    return await GoalsController.delete_goals(goal_id, user)

@router.put("/goals/{goal_id}")
async def achieve_goals(goal_id, request: Request, user: str = Depends(verify_token)):
    return await GoalsController.achieve_goals(goal_id,request, user)

@router.post("/savings/add")
async def add_savings(request: Request, user: str = Depends(verify_token)):
    return await GoalsController.add_savings(request, user)

@router.get("/savings")
async def return_savings(goal_id:str = Query(...), user: str = Depends(verify_token)):
    return await GoalsController.return_savings(goal_id, user)