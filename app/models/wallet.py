"""Wallet model - stores encrypted private keys."""

import uuid
from datetime import datetime

from sqlalchemy import String, Float, Boolean, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Wallet(Base):
    """Wallet with AES-256-GCM encrypted private key."""

    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), unique=True, nullable=False
    )

    # Public info
    wallet_address: Mapped[str] = mapped_column(String(42), nullable=False)
    label: Mapped[str] = mapped_column(String(64), default="Default")

    # Encrypted private key components
    encrypted_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    key_salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    key_iv: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    key_tag: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # Balance cache
    usdc_balance: Mapped[float] = mapped_column(Float, default=0.0)
    matic_balance: Mapped[float] = mapped_column(Float, default=0.0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Wallet address={self.wallet_address} user_id={self.user_id}>"
