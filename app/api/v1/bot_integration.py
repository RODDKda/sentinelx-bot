"""Bot integration API - verify codes and webhook endpoints."""

import secrets
import time
import string

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.user import User

router = APIRouter()

# In-memory code storage (MVP: single-process, resets on restart)
# In production, store in database
_verify_codes: dict[str, dict] = {}

CODE_LENGTH = 6
CODE_EXPIRE_SECONDS = 300  # 5 minutes


def _generate_code() -> str:
    """Generate a 6-character verification code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(CODE_LENGTH))


@router.post("/verify-code")
async def generate_verify_code(
    telegram_id: int,
    db: AsyncSession = __import__("fastapi", fromlist=["Depends"]).Depends(get_db),
):
    """Generate a one-time verification code for web dashboard login."""
    # Check user exists
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not registered. Use /start first.")

    # Generate code
    code = _generate_code()
    _verify_codes[code] = {
        "telegram_id": telegram_id,
        "user_id": user.id,
        "expires_at": time.time() + CODE_EXPIRE_SECONDS,
    }

    # Cleanup expired codes
    now = time.time()
    expired = [k for k, v in _verify_codes.items() if v["expires_at"] < now]
    for k in expired:
        del _verify_codes[k]

    return {
        "code": code,
        "expires_in": CODE_EXPIRE_SECONDS,
    }


@router.get("/verify-code/validate")
async def validate_verify_code(code: str, telegram_id: int):
    """Validate a one-time verification code."""
    entry = _verify_codes.get(code)

    if not entry:
        raise HTTPException(status_code=401, detail="Invalid or expired code.")

    if entry["telegram_id"] != telegram_id:
        raise HTTPException(status_code=403, detail="Code does not match this user.")

    if time.time() > entry["expires_at"]:
        del _verify_codes[code]
        raise HTTPException(status_code=401, detail="Code has expired.")

    # Consume the code (one-time use)
    del _verify_codes[code]

    return {
        "status": "valid",
        "user_id": entry["user_id"],
        "telegram_id": entry["telegram_id"],
    }
