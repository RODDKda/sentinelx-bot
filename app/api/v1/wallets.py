"""Wallet API routes - private key binding and management."""

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from eth_account import Account

from app.api.deps import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.core.encryption import KeyEncryption
from app.config import settings

router = APIRouter()


@router.post("/bind")
async def bind_wallet(
    private_key: str = Form(...),
    label: str = Form(default="Default"),
    telegram_id: int = Form(default=0),
    db: AsyncSession = Depends(get_db),
):
    """Bind a wallet by encrypting and storing the private key."""
    # Validate private key format
    pk = private_key.strip()
    if pk.startswith("0x"):
        pk = pk[2:]

    if len(pk) != 64:
        return f"""
        <div class="flash flash-error">
            Invalid private key. Must be 64 hex characters (with or without 0x prefix).
        </div>
        """

    try:
        # Derive wallet address
        account = Account.from_key(pk)
        wallet_address = account.address
    except Exception as e:
        return f"""
        <div class="flash flash-error">
            Invalid private key: {str(e)}
        </div>
        """

    # Find user by telegram_id (MVP: simple lookup)
    if telegram_id > 0:
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
    else:
        # Dev mode: use first user or create one
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            # Create a dev user for testing
            from app.api.v1.auth import _generate_referral_code
            user = User(
                telegram_id=999999,
                username="dev",
                referral_code=_generate_referral_code(),
            )
            db.add(user)
            await db.flush()

    if not user:
        return """
        <div class="flash flash-error">
            No user found. Please register via Telegram first.
        </div>
        """

    # Encrypt private key
    ke = KeyEncryption(settings.ENCRYPTION_KEY)
    encrypted = ke.encrypt(pk, user.id)

    # Check existing wallet
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == user.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing wallet
        existing.wallet_address = wallet_address
        existing.label = label
        existing.encrypted_key = encrypted["ciphertext"]
        existing.key_salt = encrypted["salt"]
        existing.key_iv = encrypted["iv"]
        existing.key_tag = encrypted["tag"]
        msg = "Wallet updated successfully!"
    else:
        # Create new wallet
        wallet = Wallet(
            user_id=user.id,
            wallet_address=wallet_address,
            label=label,
            encrypted_key=encrypted["ciphertext"],
            key_salt=encrypted["salt"],
            key_iv=encrypted["iv"],
            key_tag=encrypted["tag"],
        )
        db.add(wallet)
        msg = "Wallet bound successfully!"

    await db.commit()

    # Show masked address
    masked = f"{wallet_address[:6]}...{wallet_address[-4:]}"

    # Verify: decrypt and compare
    verify_msg = ""
    if existing:
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == user.id)
        )
        stored = result.scalar_one_or_none()
        if stored:
            decrypted = ke.decrypt(
                stored.encrypted_key,
                stored.key_salt,
                stored.key_iv,
                stored.key_tag,
                user.id,
            )
            verify_msg = (
                "Decryption verified." if decrypted == pk
                else "WARNING: Decryption verification failed!"
            )
    else:
        # Verify newly created wallet
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == user.id)
        )
        stored = result.scalar_one_or_none()
        if stored:
            decrypted = ke.decrypt(
                stored.encrypted_key,
                stored.key_salt,
                stored.key_iv,
                stored.key_tag,
                user.id,
            )
            verify_msg = (
                "Decryption verified." if decrypted == pk
                else "WARNING: Decryption verification failed!"
            )

    return f"""
    <div class="flash flash-success">
        <strong>{msg}</strong><br>
        Address: <code>{masked}</code><br>
        Label: {label}<br>
        Encryption: AES-256-GCM | {verify_msg}
    </div>
    <p><a href="/web/dashboard">Go to Dashboard</a></p>
    """
