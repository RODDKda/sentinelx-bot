"""Audit log model for tracking security-relevant actions."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid


class AuditLog(Base, TimestampMixin):
    """Records security-relevant actions for compliance and debugging.

    Examples: wallet binding, wallet unbinding, login attempts,
    configuration changes, trade execution.
    """

    __tablename__ = "audit_logs"

    # ── Primary Key ────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=generate_uuid
    )

    # ── Actor ──────────────────────────────────────────
    user_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True, index=True
    )
    telegram_id: Mapped[int | None] = mapped_column(
        nullable=True, index=True
    )

    # ── Action Details ─────────────────────────────────
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., "wallet.bind", "wallet.unbind", "login"
    target: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # e.g., wallet_id
    detail: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON or plain text

    # ── Source ─────────────────────────────────────────
    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True
    )  # IPv4 or IPv6

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id!r}, action={self.action!r}, "
            f"user_id={self.user_id!r})>"
        )
