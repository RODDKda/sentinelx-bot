# SentinelX MVP

Security-Enhanced Polymarket Telegram Trading Bot — Minimal Viable Product.

## Quick Start

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd sentinelx-mvp

# Python backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
```

### 2. Run Locally

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open http://localhost:8000

### 3. Deploy to Railway

```bash
# 1. Install Railway CLI
# https://docs.railway.app/guides/cli

# 2. Login
railway login

# 3. Create new project
railway init

# 4. Set environment variables (Railway dashboard or CLI)
railway variables set ENCRYPTION_KEY=$(python -c "import os; print(os.urandom(32).hex())")
railway variables set TELEGRAM_BOT_TOKEN=your_bot_token
railway variables set WEB_APP_URL=https://your-app.up.railway.app

# 5. Deploy (Railway auto-detects Dockerfile)
railway up

# 6. Get your app URL
railway domain
```

Railway auto-detects the Dockerfile and sets `$PORT` automatically.
After deployment, update `bot/wrangler.toml` with your Railway URL.

### 4. Deploy Telegram Bot

```bash
cd bot
npm install
# Edit wrangler.toml: set API_BASE_URL to your Railway URL
npx wrangler deploy
```

## Architecture

```
Telegram User → Bot (grammY/CF Workers) → API (FastAPI/Railway) → SQLite
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Home page |
| GET | `/web/dashboard` | User dashboard |
| POST | `/api/v1/auth/register` | Register via Telegram |
| POST | `/api/v1/wallet/bind` | Bind encrypted wallet |
| GET | `/api/v1/markets/active` | Active markets |
| POST | `/api/v1/trades/buy` | Place buy order |
| POST | `/api/v1/trades/sell` | Place sell order |
| POST | `/api/v1/copy/start` | Start copy trading |
| GET | `/api/v1/security/market/{slug}` | Market safety score |
| GET | `/api/v1/settings/calculate` | Fee calculation |

## Security

- AES-256-GCM encrypted private keys at rest
- HKDF-SHA256 key derivation
- User ID as AAD (binds ciphertext to user)
- Master key via Railway variables (never in code)

## License

MIT
