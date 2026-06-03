"""
Startup script for Railway - initialize DB tables directly before uvicorn.
This ensures the app is ready to accept connections immediately.
"""
import sys
import os

# Patch: create tables synchronously before the async app starts
from pathlib import Path
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

import sqlite3
db_path = data_dir / "sentinelx.db"
conn = sqlite3.connect(str(db_path))
conn.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    language TEXT DEFAULT 'en',
    referral_code TEXT UNIQUE NOT NULL,
    referred_by TEXT,
    tier TEXT DEFAULT 'free',
    fee_rate REAL DEFAULT 0.0075,
    monthly_volume REAL DEFAULT 0.0,
    is_banned INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS wallets (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    wallet_address TEXT NOT NULL,
    label TEXT DEFAULT 'Default',
    encrypted_key BLOB NOT NULL,
    key_salt BLOB NOT NULL,
    key_iv BLOB NOT NULL,
    key_tag BLOB NOT NULL,
    usdc_balance REAL DEFAULT 0.0,
    matic_balance REAL DEFAULT 0.0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
""")
conn.commit()
conn.close()
print(f"[PreInit] SQLite tables ready at {db_path}", flush=True)

# Now start uvicorn
import uvicorn
port = int(os.environ.get("PORT", "8080"))
print(f"[PreInit] Starting uvicorn on 0.0.0.0:{port}", flush=True)
uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
