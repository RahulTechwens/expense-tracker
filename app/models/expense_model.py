from pydantic import BaseModel # type: ignore
from typing import Optional


from pydantic import BaseModel
from typing import List, Optional

class ExpenseRequest(BaseModel):
    cat: str
    merchant: str
    acct: str
    bank: str
    date: str
    body: Optional[str] = None
    amount: int
    type: str
    method: str
    manual: bool
    keywords: Optional[List[str]] = []
    vector: Optional[List[float]] = []

# Example
'''
    {
        "cat": "food",
        "merchant": "Swiggy",
        "acct": "XXXX4567",
        "bank": "ICICI",
        "date": "2024-08-05",
        "body": "Food delivery from Swiggy",
        "amount": 100,
        "type": "CREDIT",
        "method": "UPI",
        "manual": false,
        "keywords": [],
        "vector": []
    }
'''
