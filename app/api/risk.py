from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

# ✅ Correct import
from app.api.transaction import TRANSACTIONS

router = APIRouter(tags=["Risk Engine"])


class RiskResponse(BaseModel):
    transaction_id: str
    risk_score: int
    risk_level: str
    reasons: List[str]


def compute_risk(transaction: dict) -> RiskResponse:
    score = 0
    reasons = []

    amount = transaction["amount"]
    user_id = transaction["user_id"]
    location = transaction["location"]
    timestamp = transaction["timestamp"]  # this is a datetime object

    # Rule 1: High transaction amount
    if amount > 5000:
        score += 30
        reasons.append("High transaction amount")

    # Rule 2: Transaction velocity (last 10 minutes)
    recent_txns = [
        t for t in TRANSACTIONS
        if t["user_id"] == user_id
        and t["timestamp"] >= timestamp - timedelta(minutes=10)
    ]

    if len(recent_txns) > 3:
        score += 25
        reasons.append("High transaction frequency")

    # Rule 3: Location anomaly
    previous_locations = {
        t["location"] for t in TRANSACTIONS if t["user_id"] == user_id
    }

    if location not in previous_locations and len(previous_locations) > 0:
        score += 20
        reasons.append("Transaction from new location")

    # Rule 4: Odd-hour transaction
    hour = timestamp.hour
    if hour < 5 or hour > 23:
        score += 15
        reasons.append("Transaction at unusual hour")

    # Cap score
    score = min(score, 100)

    # Risk level
    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return RiskResponse(
        transaction_id=transaction["transaction_id"],
        risk_score=score,
        risk_level=level,
        reasons=reasons
    )


@router.get("/{transaction_id}", response_model=RiskResponse)
def assess_risk(transaction_id: str):
    txn = next(
        (t for t in TRANSACTIONS if t["transaction_id"] == transaction_id),
        None
    )

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return compute_risk(txn)
