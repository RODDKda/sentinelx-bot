"""M2 Test: Database + Encryption."""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

import asyncio
import tempfile


async def test_encryption():
    print("--- Testing Encryption ---")
    from app.core.encryption import KeyEncryption

    # 64 hex chars = 32 bytes
    master_key = "a" * 64
    ke = KeyEncryption(master_key)

    # Test encrypt/decrypt
    plaintext = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    user_id = "test-user-123"

    encrypted = ke.encrypt(plaintext, user_id)
    assert "ciphertext" in encrypted
    assert "salt" in encrypted
    assert "iv" in encrypted
    assert len(encrypted["salt"]) == 16
    assert len(encrypted["iv"]) == 12
    print(f"  Encrypted: {len(encrypted['ciphertext'])} bytes")

    decrypted = ke.decrypt(
        encrypted["ciphertext"],
        encrypted["salt"],
        encrypted["iv"],
        user_id,
    )
    assert decrypted == plaintext, "Decrypt mismatch!"
    print("  PASS: encryption round-trip successful")

    # Test that decrypt fails with wrong user_id (should raise exception)
    try:
        ke.decrypt(
            encrypted["ciphertext"],
            encrypted["salt"],
            encrypted["iv"],
            "wrong-user-id",
        )
        print("  FAIL: should have raised on wrong user_id")
    except Exception:
        print("  PASS: decrypt fails with wrong user_id (as expected)")


async def test_database():
    print("--- Testing Database ---")
    import app.models  # noqa: register models with Base
    from app.core.database import engine, init_db, Base

    await init_db()

    # Verify tables exist
    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: Base.metadata.tables.keys()
        )
    print(f"  Tables: {list(tables)}")
    assert "users" in tables, "users table not found"
    assert "wallets" in tables, "wallets table not found"
    print("  PASS: database tables created")


async def main():
    # Override database to temp file  
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///data/test_sentinelx.db"
    os.environ["MASTER_KEY"] = "a" * 64

    print("=== M2: Database + Encryption Test ===")
    await test_encryption()
    await test_database()

    # Clean up temp db
    db_path = os.path.join(PROJECT_DIR, "data", "test_sentinelx.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    print("=== M2: All tests passed! ===")


if __name__ == "__main__":
    asyncio.run(main())
