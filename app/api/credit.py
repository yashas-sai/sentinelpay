from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

from app.api.transaction import TRANSACTIONS
from app.api.risk import compute_risk

router = APIRouter(tags=["Credit Scoring"])


class CreditScoreResponse(BaseModel):
    user_id: str
    credit_score: int
    grade: str
    factors: List[str]


@router.get("/{user_id}", response_model=CreditScoreResponse)
def get_credit_score(user_id: str):
    user_txns = [t for t in TRANSACTIONS if t["user_id"] == user_id]

    # No history → neutral score
    if not user_txns:
        return CreditScoreResponse(
            user_id=user_id,
            credit_score=600,
            grade="NEUTRAL",
            factors=["No transaction history available"]
        )

    score = 600
    factors = []

    # Consistency
    if len(user_txns) >= 10:
        score += 50
        factors.append("Consistent transaction history")

    # Risk behavior
    risk_scores = [compute_risk(t).risk_score for t in user_txns]
    avg_risk = sum(risk_scores) / len(risk_scores)

    if avg_risk < 30:
        score += 100
        factors.append("Low-risk behavior")
    elif avg_risk > 60:
        score -= 100
        factors.append("High-risk transaction patterns")

    # Spending discipline
    avg_amount = sum(t["amount"] for t in user_txns) / len(user_txns)
    if avg_amount < 2000:
        score += 50
        factors.append("Responsible spending behavior")

    # Recent activity
    last_txn_time = max(t["timestamp"] for t in user_txns)
    if last_txn_time >= datetime.utcnow() - timedelta(days=7):
        score += 50
        factors.append("Recent financial activity")

    # Clamp score
    score = max(300, min(score, 900))

    # Grade
    if score >= 750:
        grade = "EXCELLENT"
    elif score >= 650:
        grade = "GOOD"
    elif score >= 550:
        grade = "FAIR"
    else:
        grade = "POOR"

    return CreditScoreResponse(
        user_id=user_id,
        credit_score=score,
        grade=grade,
        factors=factors
    )
