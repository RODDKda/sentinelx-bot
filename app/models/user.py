"""User model."""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="en")
    referral_code: Mapped[str] = mapped_column(
        String(16), unique=True, nullable=False
    )
    referred_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    tier: Mapped[str] = mapped_column(String(16), default="free")
    fee_rate: Mapped[float] = mapped_column(Float, default=0.0075)
    monthly_volume: Mapped[float] = mapped_column(Float, default=0.0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<User id={self.id} telegram_id={self.telegram_id}>"
