"""i18n API routes + Fee Engine API."""

from fastapi import APIRouter
from app.engine.fee_engine import FeeEngine

router = APIRouter()


@router.get("/calculate")
async def calculate_fee(
    amount: float,
    tier: str = "free",
    subscription: str = "",
):
    """Calculate the fee for a given trade amount."""
    sub = subscription if subscription in ("premium", "pro") else None
    result = FeeEngine.calculate_fee(amount, tier, sub)
    commission = FeeEngine.calculate_referral_commission(result["fee"])
    return {**result, "commission": commission}


@router.get("/tiers")
async def list_tiers():
    """List all fee tiers."""
    return {
        "free": {"rate": 0.0075, "requirement": "None"},
        "vip1": {"rate": 0.0060, "requirement": "Monthly volume $50K+"},
        "vip2": {"rate": 0.0045, "requirement": "Monthly volume $250K+"},
        "vip3": {"rate": 0.0030, "requirement": "Monthly volume $1M+"},
        "premium": {"rate": 0.0065, "requirement": "$49/month subscription"},
        "pro": {"rate": 0.0055, "requirement": "$149/month subscription"},
        "min": {"rate": 0.0015, "requirement": "Absolute minimum"},
    }


@router.get("/referral")
async def referral_info():
    """Get referral program info."""
    return {
        "direct": "25% of trading fees",
        "second_level": "10% of trading fees",
    }


@router.get("/languages")
async def list_languages():
    """List supported languages."""
    return {
        "languages": [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "zh", "name": "Chinese", "native": "中文"},
        ]
    }


@router.post("/user/language")
async def set_language(telegram_id: int, language: str):
    """Set user language preference (mock)."""
    if language not in ("en", "zh"):
        return {"error": "Unsupported language. Use 'en' or 'zh'."}
    return {"status": "ok", "telegram_id": telegram_id, "language": language}
