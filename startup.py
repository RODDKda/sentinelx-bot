"""
Startup script for Railway - maximum defensive startup.
"""
import sys, os, traceback

port = os.environ.get("PORT", "8080")
print(f"[STARTUP] PORT env: {os.environ.get('PORT', 'NOT SET')}", flush=True)
print(f"[STARTUP] Will bind to 0.0.0.0:{port}", flush=True)

# Pre-create database synchronously
try:
    from pathlib import Path
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    import sqlite3
    conn = sqlite3.connect(str(data_dir / "sentinelx.db"))
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT, language TEXT DEFAULT 'en',
        referral_code TEXT UNIQUE NOT NULL, tier TEXT DEFAULT 'free',
        fee_rate REAL DEFAULT 0.0075, monthly_volume REAL DEFAULT 0.0,
        is_banned INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS wallets (
        id TEXT PRIMARY KEY, user_id TEXT UNIQUE NOT NULL,
        wallet_address TEXT NOT NULL, label TEXT DEFAULT 'Default',
        encrypted_key BLOB NOT NULL, key_salt BLOB NOT NULL,
        key_iv BLOB NOT NULL, key_tag BLOB NOT NULL,
        usdc_balance REAL DEFAULT 0.0, matic_balance REAL DEFAULT 0.0,
        is_active INTEGER DEFAULT 1, created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)
    conn.commit(); conn.close()
    print(f"[STARTUP] SQLite ready", flush=True)
except Exception as e:
    print(f"[STARTUP] DB error (non-fatal): {e}", flush=True)

# Try loading app to catch import errors early
try:
    from app.main import app
    print(f"[STARTUP] App loaded: {app.title}", flush=True)
except Exception as e:
    print(f"[STARTUP] APP LOAD ERROR: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

import uvicorn
print(f"[STARTUP] Starting server on 0.0.0.0:{port}", flush=True)
uvicorn.run(app, host="0.0.0.0", port=int(port), log_level="info")
