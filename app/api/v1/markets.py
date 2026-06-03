"""Market data API routes - powered by DataFeed for real-time freshness."""

from fastapi import APIRouter
from app.engine.data_feed import data_feed

router = APIRouter()


@router.get("/active")
async def get_active_markets():
    """Get all active markets with real-time data freshness from DataFeed."""
    markets = data_feed.get_all_markets()
    return {
        "markets": markets,
        "count": len(markets),
        "cached_at": markets[0]["cached_at"] if markets else 0,
    }


@router.get("/{slug}")
async def get_market(slug: str):
    """Get detailed market data with freshness info."""
    market = data_feed.get_market(slug)
    if not market:
        return {"error": "Market not found", "slug": slug}
    return market
