"""Trade API routes (mock for MVP, no real blockchain)."""

import uuid
import time
from fastapi import APIRouter
from app.engine.data_feed import data_feed
from app.engine.fee_engine import FeeEngine
from app.engine.copy_manager import copy_manager
from app.security_engine.detection import ManipulationDetector, FalsePositiveStrategy

router = APIRouter()

# In-memory trade log
_trades = []
_positions = {}


@router.post("/buy")
async def place_buy_order(
    market_slug: str,
    direction: str,
    amount_usd: float,
    telegram_id: int = 0,
    security_strategy: str = "advisory",
):
    """Place a buy order with real market price, fee, and security checks."""
    if direction not in ("UP", "DOWN"):
        return {"error": "Direction must be UP or DOWN"}

    # 1. Check data freshness
    can_trade, reason = data_feed.can_trade(market_slug)
    if not can_trade:
        return {
            "error": f"Data stale: {reason}",
            "action": "Retry when market data is fresh",
        }

    # 2. Get real market price
    market = data_feed.get_market(market_slug)
    if not market:
        return {"error": "Market not found"}

    price = market["up_ask"] if direction == "UP" else market["down_ask"]
    data_age = max(market["up_age_sec"], market["down_age_sec"])

    # 3. Security check
    detection = ManipulationDetector.analyze(
        market_slug, market["volume"], market["up_ask"], market["down_ask"]
    )
    fp = FalsePositiveStrategy.evaluate(detection, strategy=security_strategy)
    if not fp["can_trade"]:
        return {
            "error": fp["message"],
            "safety_score": detection["overall"],
            "action": "Use a different market or lower your risk threshold",
        }

    # 4. Calculate fee
    fee_result = FeeEngine.calculate_fee(amount_usd)

    contracts = amount_usd / price

    order = {
        "order_id": str(uuid.uuid4())[:8],
        "market_slug": market_slug,
        "direction": direction,
        "contracts": round(contracts, 2),
        "price": price,
        "total_usd": amount_usd,
        "fee": fee_result["fee"],
        "fee_rate": fee_result["rate"],
        "fee_breakdown": fee_result["breakdown"],
        "status": "filled",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "telegram_id": telegram_id,
        "data_age_sec": round(data_age, 1),
        "data_freshness": market["data_freshness"],
        "safety_score": detection["overall"],
        "safety_strategy": fp["strategy_used"],
        "safety_warning": fp.get("message", ""),
    }
    _trades.append(order)

    # Track position
    key = f"{market_slug}:{direction}"
    if key in _positions:
        _positions[key]["contracts"] += contracts
        _positions[key]["invested"] += amount_usd
    else:
        _positions[key] = {
            "market_slug": market_slug,
            "direction": direction,
            "contracts": contracts,
            "avg_price": price,
            "invested": amount_usd,
        }

    # 5. Trigger copy trades if this user is a leader
    leader_id = str(telegram_id) if telegram_id else "0"
    copy_results = copy_manager.on_leader_trade(
        leader_id=leader_id,
        market_slug=market_slug,
        direction=direction,
        amount_usd=amount_usd,
        price=price,
    )

    return {
        "status": "ok",
        "order": order,
        "copy_trades_triggered": len([r for r in copy_results if r["status"] == "executed"]),
    }


@router.post("/sell")
async def place_sell_order(market_slug: str, telegram_id: int = 0):
    """Place a mock sell order."""
    # Find position
    pos_key_up = f"{market_slug}:UP"
    pos_key_down = f"{market_slug}:DOWN"

    sold = []
    for key in [pos_key_up, pos_key_down]:
        if key in _positions:
            pos = _positions[key]
            sell_price = 0.62 if pos["direction"] == "UP" else 0.40
            revenue = pos["contracts"] * sell_price
            pnl = revenue - pos["invested"]
            order = {
                "order_id": str(uuid.uuid4())[:8],
                "market_slug": market_slug,
                "direction": pos["direction"],
                "contracts": round(pos["contracts"], 2),
                "price": sell_price,
                "revenue": round(revenue, 4),
                "pnl": round(pnl, 4),
                "status": "filled",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            _trades.append(order)
            sold.append(order)
            del _positions[key]

    if not sold:
        return {"error": "No position found for this market"}

    return {"status": "ok", "sold": sold}


@router.get("/history")
async def get_trade_history(telegram_id: int = 0):
    """Get trade history."""
    return {"trades": _trades[-20:], "total": len(_trades)}


@router.get("/positions")
async def get_positions(telegram_id: int = 0):
    """Get current positions."""
    total_invested = sum(p["invested"] for p in _positions.values())
    return {
        "positions": list(_positions.values()),
        "total_invested": round(total_invested, 2),
    }
