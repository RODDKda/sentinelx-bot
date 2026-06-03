"""
Fee Engine - Tiered fee calculation with referral commissions.

Fee Tiers:
  Free:    0.75%
  VIP1:    0.60%  (monthly volume $50K+)
  VIP2:    0.45%  (monthly volume $250K+)
  VIP3:    0.30%  (monthly volume $1M+)
  Premium: 0.65%  ($49/mo subscription, pre-discount)
  Pro:     0.55%  ($149/mo, pre-discount)

Referral: 25% direct + 10% second-level
"""

from typing import Tuple


class FeeEngine:
    """Calculate trading fees and referral commissions."""

    # Base tiers
    DEFAULT_FEE = 0.0075

    VIP_TIERS = {
        "vip1": 0.0060,
        "vip2": 0.0045,
        "vip3": 0.0030,
    }

    # Subscription discounts (stacked on VIP)
    SUBSCRIPTION_DISCOUNT = {
        "premium": 0.0010,
        "pro": 0.0020,
    }

    MIN_FEE_RATE = 0.0015  # 0.15% absolute minimum

    # Referral rates
    DIRECT_REFERRAL_RATE = 0.25
    SECOND_LEVEL_RATE = 0.10

    @classmethod
    def calculate_fee(
        cls,
        trade_amount_usd: float,
        user_tier: str = "free",
        subscription_tier: str | None = None,
    ) -> dict:
        """
        Calculate fee for a trade.

        Returns:
            {
                "rate": float,        # final fee rate
                "fee": float,         # fee in USD
                "breakdown": str,     # human-readable
            }
        """
        rate = cls.DEFAULT_FEE

        # Apply VIP tier discount
        vip_rate = cls.VIP_TIERS.get(user_tier, cls.DEFAULT_FEE)
        rate = min(rate, vip_rate)

        # Apply subscription discount
        if subscription_tier and subscription_tier in cls.SUBSCRIPTION_DISCOUNT:
            rate -= cls.SUBSCRIPTION_DISCOUNT[subscription_tier]

        # Floor
        rate = max(cls.MIN_FEE_RATE, rate)

        fee = trade_amount_usd * rate

        return {
            "rate": round(rate, 4),
            "fee": round(fee, 4),
            "breakdown": cls._breakdown(user_tier, subscription_tier, rate),
        }

    @classmethod
    def calculate_referral_commission(cls, fee_usd: float) -> dict:
        """
        Calculate referral commissions.

        Returns:
            {
                "direct": float,      # 25% to direct referrer
                "second_level": float, # 10% to second-level referrer
                "platform": float,     # what the platform keeps
            }
        """
        direct = round(fee_usd * cls.DIRECT_REFERRAL_RATE, 4)
        second = round(fee_usd * cls.SECOND_LEVEL_RATE, 4)
        platform = round(fee_usd - direct - second, 4)

        return {
            "direct": direct,
            "second_level": second,
            "platform": platform,
        }

    @classmethod
    def _breakdown(cls, tier: str, sub: str | None, rate: float) -> str:
        """Human-readable fee breakdown."""
        parts = [f"Base: {cls.DEFAULT_FEE*100:.2f}%"]
        if tier in cls.VIP_TIERS:
            parts.append(f"VIP({tier}): -{(cls.DEFAULT_FEE - cls.VIP_TIERS[tier])*100:.2f}%")
        if sub:
            parts.append(f"Sub({sub}): -{cls.SUBSCRIPTION_DISCOUNT[sub]*100:.2f}%")
        parts.append(f"= {rate*100:.2f}%")
        return " | ".join(parts)
