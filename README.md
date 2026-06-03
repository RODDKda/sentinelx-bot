# SentinelX MVP

Security-Enhanced Polymarket Telegram Trading Bot — Minimal Viable Product.

## Quick Start

### 1. Clone & Setup

```bash
cd sentinelx-mvp

# Python backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Edit .env: set ENCRYPTION_KEY, JWT_SECRET, TELEGRAM_BOT_TOKEN
```

### 2. Run Backend

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Verify: `curl http://localhost:8000/health` → `{"status":"ok","version":"0.1.0"}`

### 3. Run Telegram Bot

```bash
cd bot
npm install
TELEGRAM_BOT_TOKEN=your_token npx tsx src/bot.ts
```

Commands: `/start /help /markets /web /ping`

### 4. Deploy to fly.io

```bash
# Install flyctl: https://fly.io/docs/flyctl/install/
fly auth signup
fly launch
fly volumes create sentinelx_data --size 1 --region hkg
fly secrets set ENCRYPTION_KEY=$(python -c "import os; print(os.urandom(32).hex())")
fly secrets set TELEGRAM_BOT_TOKEN=your_bot_token
fly deploy
```

## Architecture

```
Telegram User → Bot (grammY) → API (FastAPI) → SQLite (encrypted keys)
                  ↓ Cloudflare         ↓ fly.io         ↓ Persistent Volume
```

- **Website** (fly.io): User management, wallet binding, dashboard
- **Telegram Bot** (grammY + CF Workers): Command-line trading interface
- **Database** (SQLite): Single file, AES-256-GCM encrypted private keys

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Home page |
| GET | `/web/dashboard` | User dashboard |
| GET | `/web/wallet/bind` | Wallet binding form |
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/wallet/bind` | Bind encrypted wallet |
| POST | `/api/v1/bot/verify-code` | Generate web login code |
| GET | `/api/v1/bot/verify-code/validate` | Validate login code |

## Security

- Private keys encrypted with AES-256-GCM at rest
- HKDF-SHA256 key derivation from master encryption key
- User ID as AAD binds ciphertext to specific user
- Master key stored via fly.io secrets (never in code)
- Private keys only decrypted in memory during transaction signing

## Cost

| Resource | Monthly |
|----------|---------|
| fly.io VM (256MB) | $2.02 |
| fly.io Volume (1GB) | $0.15 |
| Cloudflare Workers | Free (10M req) |
| **Total** | **~$2.17** |

First 2 months free with $5 signup credit.

## License

MIT
