"""
Copy Trading Manager
====================
Manages copy-trade relationships between users.
When a leader executes a trade, all followers mirror it proportionally.
"""

import uuid
import time
from typing import Optional
from threading import Lock


class CopyTradeManager:
    """In-memory copy trade manager (MVP)."""

    def __init__(self):
        self._lock = Lock()
        # {follower_id: [{leader_id, max_per_trade, total_cap, copy_ratio, is_active}]}
        self._relationships: dict[str, list[dict]] = {}
        # Trade log
        self._copy_trades: list[dict] = []

    def start_copying(
        self,
        follower_id: str,
        leader_id: str,
        max_per_trade: float = 100.0,
        total_cap: float = 1000.0,
        copy_ratio: float = 1.0,
    ) -> dict:
        """Start copying a leader."""
        with self._lock:
            if follower_id not in self._relationships:
                self._relationships[follower_id] = []

            # Check duplicate
            for rel in self._relationships[follower_id]:
                if rel["leader_id"] == leader_id:
                    # Update existing
                    rel["max_per_trade"] = max_per_trade
                    rel["total_cap"] = total_cap
                    rel["copy_ratio"] = copy_ratio
                    rel["is_active"] = True
                    return {"status": "updated", **rel}

            # Create new
            rel = {
                "id": str(uuid.uuid4())[:8],
                "follower_id": follower_id,
                "leader_id": leader_id,
                "max_per_trade": max_per_trade,
                "total_cap": total_cap,
                "copy_ratio": copy_ratio,
                "total_copied": 0.0,
                "is_active": True,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            self._relationships[follower_id].append(rel)
            return {"status": "created", **rel}

    def stop_copying(self, follower_id: str, leader_id: str) -> dict:
        """Stop copying a leader."""
        with self._lock:
            if follower_id not in self._relationships:
                return {"status": "not_found"}
            for rel in self._relationships[follower_id]:
                if rel["leader_id"] == leader_id:
                    rel["is_active"] = False
                    return {"status": "stopped", **rel}
            return {"status": "not_found"}

    def get_following(self, follower_id: str) -> list[dict]:
        """Get all leaders a user is following."""
        with self._lock:
            return self._relationships.get(follower_id, [])

    def get_followers(self, leader_id: str) -> list[dict]:
        """Get all followers of a leader."""
        with self._lock:
            result = []
            for follower_id, rels in self._relationships.items():
                for rel in rels:
                    if rel["leader_id"] == leader_id and rel["is_active"]:
                        result.append(rel)
            return result

    def on_leader_trade(
        self,
        leader_id: str,
        market_slug: str,
        direction: str,
        amount_usd: float,
        price: float,
    ) -> list[dict]:
        """
        Triggered when a leader makes a trade.
        Returns list of copy trades that should be executed for followers.
        """
        followers = self.get_followers(leader_id)
        if not followers:
            return []

        results = []
        with self._lock:
            for rel in followers:
                # Calculate copy amount
                copy_amount = min(
                    amount_usd * rel["copy_ratio"],
                    rel["max_per_trade"],
                )

                # Check cap
                remaining = rel["total_cap"] - rel["total_copied"]
                if remaining <= 0:
                    results.append({
                        "follower_id": rel["follower_id"],
                        "status": "skipped",
                        "reason": "cap_reached",
                    })
                    continue

                copy_amount = min(copy_amount, remaining)

                if copy_amount < 1.0:
                    results.append({
                        "follower_id": rel["follower_id"],
                        "status": "skipped",
                        "reason": "dust",
                    })
                    continue

                # Record
                contracts = copy_amount / price
                rel["total_copied"] += copy_amount

                copy_trade = {
                    "id": str(uuid.uuid4())[:8],
                    "follower_id": rel["follower_id"],
                    "leader_id": leader_id,
                    "market_slug": market_slug,
                    "direction": direction,
                    "amount_usd": round(copy_amount, 2),
                    "contracts": round(contracts, 2),
                    "price": price,
                    "copy_ratio": rel["copy_ratio"],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                self._copy_trades.append(copy_trade)
                results.append({"follower_id": rel["follower_id"], "status": "executed", "trade": copy_trade})

        return results

    def get_copy_trade_history(self, follower_id: Optional[str] = None) -> list[dict]:
        """Get copy trade history, optionally filtered by follower."""
        if follower_id:
            return [t for t in self._copy_trades if t["follower_id"] == follower_id]
        return self._copy_trades[-50:]

    def get_leader_stats(self, leader_id: str) -> dict:
        """Get stats for a leader (for the leaderboard)."""
        trades = [t for t in self._copy_trades if t["leader_id"] == leader_id]
        followers = self.get_followers(leader_id)
        return {
            "leader_id": leader_id,
            "follower_count": len(followers),
            "total_copy_volume": round(sum(t["amount_usd"] for t in trades), 2),
            "copy_trade_count": len(trades),
        }


# Global instance
copy_manager = CopyTradeManager()
