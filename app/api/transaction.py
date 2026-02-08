from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid

router = APIRouter()

# -----------------------------
# In-memory transaction store
# (Later replace with DB)
# -----------------------------
TRANSACTIONS = []


# -----------------------------
# Transaction Input Schema
# -----------------------------
class TransactionInput(BaseModel):
    user_id: str = Field(..., example="user_123")
    amount: float = Field(..., gt=0, example=2500.50)
    merchant: str = Field(..., example="Amazon")
    category: str = Field(..., example="E_COMMERCE")
    location: str = Field(..., example="Bangalore")
    device_id: str = Field(..., example="device_xyz")


# -----------------------------
# Transaction Output Schema
# -----------------------------
class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    received_at: datetime


# -----------------------------
# POST /transaction/
# -----------------------------
@router.post("/", response_model=TransactionResponse)
async def ingest_transaction(transaction: TransactionInput):
    """
    Ingest a transaction into SentinelPay.
    This will later trigger:
    - Risk analysis
    - Dynamic limit checks
    - Credit behavior tracking
    """

    transaction_record = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": transaction.user_id,
        "amount": transaction.amount,
        "merchant": transaction.merchant,
        "category": transaction.category,
        "location": transaction.location,
        "device_id": transaction.device_id,
        "timestamp": datetime.utcnow()
    }

    TRANSACTIONS.append(transaction_record)

    return {
        "transaction_id": transaction_record["transaction_id"],
        "status": "accepted",
        "received_at": transaction_record["timestamp"]
    }


# -----------------------------
# GET /transaction/all
# (Debug / Demo purpose)
# -----------------------------
@router.get("/all")
async def get_all_transactions() -> List[dict]:
    """
    Fetch all ingested transactions.
    Used for demos, testing, and analysis.
    """
    return TRANSACTIONS
