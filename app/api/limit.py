from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.api.transaction import TRANSACTIONS
from app.api.risk import compute_risk

router = APIRouter(tags=["Dynamic Limits"])


# -----------------------------
# Mock user base limits
# -----------------------------
BASE_LIMITS = {
    "default": 10000
}


class LimitResponse(BaseModel):
    user_id: str
    base_limit: float
    adjusted_limit: float
    decision: str
    reasons: List[str]


@router.get("/{user_id}", response_model=LimitResponse)
def get_dynamic_limit(user_id: str):
    user_txns = [t for t in TRANSACTIONS if t["user_id"] == user_id]

    base_limit = BASE_LIMITS.get(user_id, BASE_LIMITS["default"])
    adjusted_limit = base_limit
    reasons = []

    if not user_txns:
        return LimitResponse(
            user_id=user_id,
            base_limit=base_limit,
            adjusted_limit=base_limit,
            decision="ALLOW",
            reasons=["No risky behavior detected"]
        )

    # Analyze recent risk
    recent_txns = user_txns[-5:]
    risk_scores = [compute_risk(t).risk_score for t in recent_txns]
    avg_risk = sum(risk_scores) / len(risk_scores)

    if avg_risk >= 70:
        adjusted_limit *= 0.3
        reasons.append("High average risk detected")
        decision = "BLOCK"
    elif avg_risk >= 40:
        adjusted_limit *= 0.6
        reasons.append("Moderate risk detected")
        decision = "WARN"
    else:
        reasons.append("Low risk behavior")
        decision = "ALLOW"

    return LimitResponse(
        user_id=user_id,
        base_limit=base_limit,
        adjusted_limit=adjusted_limit,
        decision=decision,
        reasons=reasons
    )
