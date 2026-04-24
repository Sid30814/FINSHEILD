"""
FinShield - Transaction Models
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class TransactionCreate(BaseModel):
    sender_account: str = Field(..., example="ACC-001234")
    receiver_account: str = Field(..., example="ACC-005678")
    amount: float = Field(..., gt=0, le=1_000_000, example=500.00)
    transaction_type: str = Field(default="transfer", example="transfer")
    currency: str = Field(default="USD", max_length=3)
    metadata: Optional[dict] = None


class TransactionResponse(BaseModel):
    transaction_id: str
    sender_account: str
    receiver_account: str
    amount: float
    currency: str
    transaction_type: str
    status: str
    fraud_score: float
    timestamp: str
    message: str


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
