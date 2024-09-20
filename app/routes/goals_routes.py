from app.models.expense_model import Expense
from fastapi import APIRouter, Query, Request # type: ignore
from typing import Optional
from app.controller.goal_controller import GoalsController

router = APIRouter()

@router.get("/goals")
async def return_goals(
    request: Request,
    goal_id: Optional[str] = Query(None, alias="goal_id"),
):
    return await GoalsController.return_goals(goal_id)

@router.post("/goals/add")
async def add_goals(request: Request):
    return await GoalsController.add_goals(request)

@router.delete("/goals/delete")
async def delete_goals(goal_ids:str = Query(...)):
    return await GoalsController.delete_goals(goal_ids)

@router.post("/savings/add")
async def add_savings(request: Request):
    return await GoalsController.add_savings(request)

@router.get("/savings")
async def return_savings(goal_id:str = Query(...)):
    return await GoalsController.return_savings(goal_id)