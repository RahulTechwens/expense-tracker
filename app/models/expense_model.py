# app/models/expense_model.py

from pydantic import BaseModel
from typing import Optional


class ExpenseRequest(BaseModel): 
    amount:float
    description: str