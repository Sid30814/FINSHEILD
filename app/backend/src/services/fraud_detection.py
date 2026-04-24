"""
FinShield - Fraud Detection Service
Rule-based + statistical fraud scoring for financial transactions
"""

import math
import random
from utils.logger import get_structured_logger

logger = get_structured_logger("finshield.fraud")


class FraudDetectionService:
    """
    Multi-rule fraud detection engine.
    Returns a fraud_score between 0.0 (clean) and 1.0 (highly suspicious).
    """

    HIGH_RISK_THRESHOLD = 50_000
    VELOCITY_WINDOW = 10   # In-memory: last N transactions
    _recent: list = []

    def score(self, amount: float, sender: str, receiver: str, tx_type: str) -> float:
        score = 0.0
        reasons = []

        # Rule 1: High-value transaction
        if amount > self.HIGH_RISK_THRESHOLD:
            score += 0.4
            reasons.append("high_value")

        # Rule 2: Suspicious round numbers (money laundering pattern)
        if amount > 1000 and amount % 1000 == 0:
            score += 0.15
            reasons.append("round_amount")

        # Rule 3: Same sender/receiver (loopback)
        if sender == receiver:
            score += 0.5
            reasons.append("loopback")

        # Rule 4: Velocity — sender appearing frequently
        sender_count = sum(1 for t in self._recent if t == sender)
        if sender_count >= 3:
            score += 0.25
            reasons.append("velocity_breach")

        # Track sender
        self._recent.append(sender)
        if len(self._recent) > self.VELOCITY_WINDOW:
            self._recent.pop(0)

        # Rule 5: Withdrawal of very large amounts
        if tx_type == "withdrawal" and amount > 10_000:
            score += 0.2
            reasons.append("large_withdrawal")

        # Cap at 1.0 and add small noise for realism
        score = min(1.0, score + random.uniform(0, 0.05))

        logger.info(
            "Fraud score computed",
            extra={
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "fraud_score": round(score, 4),
                "fraud_reasons": reasons,
                "flagged": score > 0.7,
            }
        )

        return round(score, 4)


fraud_service = FraudDetectionService()
