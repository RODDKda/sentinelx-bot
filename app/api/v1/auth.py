"""Authentication API routes."""

import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.user import User

router = APIRouter()


def _generate_referral_code(length: int = 8) -> str:
    """Generate a random referral code."""
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


@router.post("/register")
async def register_user(
    telegram_id: int,
    username: str | None = None,
    referrer_code: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user via Telegram ID."""
    # Check if already registered
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {
            "status": "existing",
            "user_id": existing.id,
            "referral_code": existing.referral_code,
        }

    # Create new user
    user = User(
        telegram_id=telegram_id,
        username=username,
        referral_code=_generate_referral_code(),
        language="en",
    )

    # Handle referrer
    if referrer_code:
        ref_result = await db.execute(
            select(User).where(User.referral_code == referrer_code)
        )
        referrer = ref_result.scalar_one_or_none()
        if referrer and referrer.id != user.id:
            user.referred_by = referrer.id

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "status": "created",
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "referral_code": user.referral_code,
    }
