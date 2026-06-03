"""
Security Detection Engine
==========================
Market manipulation detection, wallet scoring, market health evaluation.
False-positive handling strategies: advisory / threshold / confidence / configurable.
"""

import random
import time
from typing import Optional


class ManipulationDetector:
    """Detect market manipulation patterns."""

    @staticmethod
    def analyze(market_slug: str, volume: float, up_price: float, down_price: float) -> dict:
        """
        Analyze market for manipulation signals.
        Returns score 0-100 and detailed breakdown.
        """
        # Volume anomaly (mock: use hash to get consistent but random-feeling score per market)
        seed = hash(market_slug + str(int(time.time() / 3600))) % 100
        volume_score = abs(seed % 40)  # 0-40 range

        # Price spread anomaly
        spread = up_price + down_price
        spread_score = 0
        if spread > 1.05:
            spread_score = 30
        elif spread > 1.02:
            spread_score = 15

        # Price extreme
        extreme_score = 0
        if up_price > 0.90 or down_price > 0.90:
            extreme_score = 25
        elif up_price > 0.80 or down_price > 0.80:
            extreme_score = 10

        # Last-minute volatility (simulated)
        last_min_score = abs(seed % 20)

        overall = min(100, volume_score + spread_score + extreme_score + last_min_score)

        return {
            "overall": overall,
            "volume_anomaly": volume_score,
            "spread_anomaly": spread_score,
            "price_extreme": extreme_score,
            "last_minute_risk": last_min_score,
            "confidence": round(random.uniform(0.6, 0.95), 2),
            "risk_level": "high" if overall > 60 else ("medium" if overall > 30 else "low"),
        }


class WalletScorer:
    """Score wallet reputation based on on-chain behavior (mock for MVP)."""

    @staticmethod
    def score(wallet_address: str) -> dict:
        """Score a wallet address."""
        seed = hash(wallet_address) % 100
        reputation = 50 + (seed % 40)  # 50-90 range
        return {
            "wallet_address": wallet_address,
            "reputation_score": reputation,
            "trading_history_days": seed % 200,
            "win_rate_estimate": round(40 + (seed % 40), 1),
            "is_verified_smart_wallet": seed > 70,
            "risk_level": "low" if reputation > 70 else ("medium" if reputation > 50 else "high"),
        }


class FalsePositiveStrategy:
    """False positive handling strategies for security alerts."""

    STRATEGIES = ["advisory", "threshold", "confidence", "configurable"]

    @staticmethod
    def evaluate(
        security_score: dict,
        strategy: str = "advisory",
        user_threshold: float = 80.0,
    ) -> dict:
        """
        Evaluate whether trading should proceed.

        Returns:
            {
                "can_trade": bool,
                "message": str,
                "risk_level": str,
                "strategy_used": str,
            }
        """
        overall = security_score["overall"]
        confidence = security_score.get("confidence", 0.7)

        if strategy == "advisory":
            return FalsePositiveStrategy._advisory(security_score)

        elif strategy == "threshold":
            return FalsePositiveStrategy._threshold(security_score, user_threshold)

        elif strategy == "confidence":
            return FalsePositiveStrategy._confidence_weighted(security_score)

        elif strategy == "configurable":
            # Free users get advisory, others get threshold
            return FalsePositiveStrategy._advisory(security_score)

        return {"can_trade": True, "message": "", "risk_level": "low", "strategy_used": strategy}

    @staticmethod
    def _advisory(scores: dict) -> dict:
        """Strategy A: Advisory only - warn but never block."""
        overall = scores["overall"]
        if overall > 80:
            return {
                "can_trade": True,
                "message": (
                    f"WARNING: High risk market (score: {overall}/100). "
                    f"Manipulation: {scores.get('volume_anomaly', '?')}/100. "
                    f"Trade at your own risk."
                ),
                "risk_level": "high",
                "strategy_used": "advisory",
            }
        elif overall > 50:
            return {
                "can_trade": True,
                "message": f"Moderate risk (score: {overall}/100). Consider reducing position.",
                "risk_level": "medium",
                "strategy_used": "advisory",
            }
        return {"can_trade": True, "message": "", "risk_level": "low", "strategy_used": "advisory"}

    @staticmethod
    def _threshold(scores: dict, user_threshold: float) -> dict:
        """Strategy B: Block when score > threshold."""
        overall = scores["overall"]
        if overall > user_threshold:
            return {
                "can_trade": False,
                "message": (
                    f"BLOCKED: Risk score {overall}/100 exceeds threshold {user_threshold}. "
                    f"Use force trade to override."
                ),
                "risk_level": "critical",
                "strategy_used": "threshold",
            }
        elif overall > 50:
            return {
                "can_trade": True,
                "message": f"Elevated risk ({overall}/100). Proceed with caution.",
                "risk_level": "medium",
                "strategy_used": "threshold",
            }
        return {"can_trade": True, "message": "", "risk_level": "low", "strategy_used": "threshold"}

    @staticmethod
    def _confidence_weighted(scores: dict) -> dict:
        """Strategy C: Weight risk by detection confidence."""
        overall = scores["overall"]
        confidence = scores.get("confidence", 0.5)
        weighted = overall * confidence
        if weighted > 60:
            return {
                "can_trade": False,
                "message": f"BLOCKED: High-confidence risk ({weighted:.0f}/100).",
                "risk_level": "critical",
                "strategy_used": "confidence",
            }
        elif overall > 50:
            return {
                "can_trade": True,
                "message": f"Some indicators detected ({weighted:.0f}/100).",
                "risk_level": "medium",
                "strategy_used": "confidence",
            }
        return {"can_trade": True, "message": "", "risk_level": "low", "strategy_used": "confidence"}
