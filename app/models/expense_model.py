from pydantic import BaseModel # type: ignore
from typing import Optional


class ExpenseRequest(BaseModel): 
    amount:float
    description: str