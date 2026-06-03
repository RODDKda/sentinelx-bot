"""Security detection API routes."""

from fastapi import APIRouter
from app.security_engine.detection import (
    ManipulationDetector,
    WalletScorer,
    FalsePositiveStrategy,
)
from app.engine.data_feed import data_feed

router = APIRouter()


@router.get("/market/{slug}")
async def check_market_safety(slug: str, strategy: str = "advisory"):
    """Get security score for a market with false-positive handling."""
    market = data_feed.get_market(slug)
    if not market:
        return {"error": "Market not found"}

    # Analyze
    detection = ManipulationDetector.analyze(
        market_slug=slug,
        volume=market["volume"],
        up_price=market["up_ask"],
        down_price=market["down_ask"],
    )

    # Apply false positive strategy
    fp_result = FalsePositiveStrategy.evaluate(detection, strategy=strategy)

    return {
        **detection,
        "can_trade": fp_result["can_trade"],
        "warning": fp_result["message"],
        "strategy_used": fp_result["strategy_used"],
        "market_slug": slug,
    }


@router.get("/strategies")
async def list_strategies():
    """List available false-positive handling strategies."""
    return {
        "strategies": [
            {"id": "advisory", "name": "Advisory Only", "desc": "Warn but never block trades"},
            {"id": "threshold", "name": "Threshold Block", "desc": "Block when risk score > 80"},
            {"id": "confidence", "name": "Confidence Weighted", "desc": "Weight risk by detection confidence"},
            {"id": "configurable", "name": "User Configurable", "desc": "User picks threshold (Premium/Pro)"},
        ]
    }


@router.get("/wallet/{address}")
async def check_wallet(address: str):
    """Get wallet reputation score."""
    return WalletScorer.score(address)
