"""
Real-time Market Data Feed
===========================
Simulates WebSocket connection to Polymarket CLOB.
Tracks price freshness with timestamps for data validation.
In production, this connects to: wss://ws-subscriptions-clob.polymarket.com/ws/market
"""

import time
import random
import threading
from typing import Dict, Optional


class DataFeed:
    """Simulated market data feed with freshness tracking."""

    # Maximum allowed age for data to be considered "live"
    MAX_DATA_AGE_SEC = 10  # After 10s, data is "stale"
    MAX_TRADE_AGE_SEC = 3  # After 3s, refuse trades

    def __init__(self):
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

        # Market state - mirrors 4coinsbot data_feed.py structure
        self.markets: Dict[str, dict] = {
            "btc-above-95k": {
                "slug": "btc-above-95k",
                "title": "BTC above $95,000 at close?",
                "coin": "BTC",
                "up_ask": 0.62,
                "down_ask": 0.40,
                "up_bid": 0.61,
                "down_bid": 0.39,
                "up_ask_ts": time.time(),
                "down_ask_ts": time.time(),
                "up_bid_ts": time.time(),
                "down_bid_ts": time.time(),
                "volume": 1250000,
                "end_time": int(time.time()) + 480,
                "safety_score": 15,
                "stale_count": 0,
            },
            "eth-above-3500": {
                "slug": "eth-above-3500",
                "title": "ETH above $3,500 at close?",
                "coin": "ETH",
                "up_ask": 0.55,
                "down_ask": 0.47,
                "up_bid": 0.54,
                "down_bid": 0.46,
                "up_ask_ts": time.time(),
                "down_ask_ts": time.time(),
                "up_bid_ts": time.time(),
                "down_bid_ts": time.time(),
                "volume": 890000,
                "end_time": int(time.time()) + 720,
                "safety_score": 22,
                "stale_count": 0,
            },
            "sol-above-180": {
                "slug": "sol-above-180",
                "title": "SOL above $180 at close?",
                "coin": "SOL",
                "up_ask": 0.48,
                "down_ask": 0.54,
                "up_bid": 0.47,
                "down_bid": 0.53,
                "up_ask_ts": time.time(),
                "down_ask_ts": time.time(),
                "up_bid_ts": time.time(),
                "down_bid_ts": time.time(),
                "volume": 450000,
                "end_time": int(time.time()) + 360,
                "safety_score": 38,
                "stale_count": 0,
            },
            "xrp-above-2": {
                "slug": "xrp-above-2",
                "title": "XRP above $2.00 at close?",
                "coin": "XRP",
                "up_ask": 0.71,
                "down_ask": 0.31,
                "up_bid": 0.70,
                "down_bid": 0.30,
                "up_ask_ts": time.time(),
                "down_ask_ts": time.time(),
                "up_bid_ts": time.time(),
                "down_bid_ts": time.time(),
                "volume": 320000,
                "end_time": int(time.time()) + 600,
                "safety_score": 8,
                "stale_count": 0,
            },
        }

    def start(self):
        """Start the simulated price feed thread."""
        self._running = True
        self._thread = threading.Thread(target=self._simulate_updates, daemon=True)
        self._thread.start()
        print("[DataFeed] Started simulated market data feed")

    def stop(self):
        """Stop the feed."""
        self._running = False
        print("[DataFeed] Stopped")

    def _simulate_updates(self):
        """Simulate WebSocket price updates every 1-3 seconds."""
        while self._running:
            time.sleep(random.uniform(1.0, 3.0))
            with self._lock:
                for slug, market in self.markets.items():
                    # Simulate small price movements
                    delta_up = random.uniform(-0.02, 0.02)
                    delta_down = random.uniform(-0.02, 0.02)
                    market["up_ask"] = round(max(0.01, min(0.99, market["up_ask"] + delta_up)), 3)
                    market["down_ask"] = round(max(0.01, min(0.99, market["down_ask"] + delta_down)), 3)
                    market["up_bid"] = round(max(0.01, market["up_ask"] - 0.01), 3)
                    market["down_bid"] = round(max(0.01, market["down_ask"] - 0.01), 3)
                    now = time.time()
                    market["up_ask_ts"] = now
                    market["down_ask_ts"] = now
                    market["up_bid_ts"] = now
                    market["down_bid_ts"] = now

    def get_market(self, slug: str) -> Optional[dict]:
        """Get market data with freshness information."""
        with self._lock:
            market = self.markets.get(slug)
            if not market:
                return None

            now = time.time()
            up_age = now - market["up_ask_ts"]
            down_age = now - market["down_ask_ts"]

            return {
                "slug": market["slug"],
                "title": market["title"],
                "coin": market["coin"],
                "up_ask": market["up_ask"],
                "down_ask": market["down_ask"],
                "up_bid": market["up_bid"],
                "down_bid": market["down_bid"],
                "spread": round(market["up_ask"] + market["down_ask"], 3),
                "volume": market["volume"],
                "ends_in_seconds": max(0, market["end_time"] - int(now)),
                "safety_score": market["safety_score"],
                # Data freshness
                "data_freshness": self._freshness_label(up_age, down_age),
                "up_age_sec": round(up_age, 1),
                "down_age_sec": round(down_age, 1),
                "is_tradeable": up_age <= self.MAX_TRADE_AGE_SEC and down_age <= self.MAX_TRADE_AGE_SEC,
                "cached_at": int(now),
            }

    def get_all_markets(self) -> list:
        """Get all markets with freshness."""
        return [self.get_market(slug) for slug in self.markets]

    def _freshness_label(self, up_age: float, down_age: float) -> str:
        """Get human-readable freshness label."""
        max_age = max(up_age, down_age)
        if max_age <= 3:
            return "live"
        elif max_age <= self.MAX_DATA_AGE_SEC:
            return "recent"
        else:
            return "stale"

    def can_trade(self, slug: str) -> tuple[bool, str]:
        """Check if market data is fresh enough to trade."""
        market = self.get_market(slug)
        if not market:
            return False, "Market not found"

        if not market["is_tradeable"]:
            age = max(market["up_age_sec"], market["down_age_sec"])
            return False, f"Data too old ({age:.1f}s > {self.MAX_TRADE_AGE_SEC}s max)"

        return True, "ok"


# Global instance
data_feed = DataFeed()
