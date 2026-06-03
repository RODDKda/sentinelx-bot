#!/bin/bash
# SentinelX MVP - Deployment Script for fly.io
# Usage: bash deploy.sh

set -e

echo "=== SentinelX MVP Deploy ==="

# Check flyctl
if ! command -v flyctl &> /dev/null; then
    echo "ERROR: flyctl not found. Install: https://fly.io/docs/flyctl/install/"
    exit 1
fi

# Check environment
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ">>> Edit .env with your settings, then re-run deploy.sh"
    exit 1
fi

# Source env (bash compatible)
set -a
source .env
set +a

echo "=== 1. Logging in ==="
fly auth whoami 2>/dev/null || fly auth login

echo "=== 2. Launching app ==="
fly launch --no-deploy --name sentinelx-mvp --region hkg 2>/dev/null || true

echo "=== 3. Creating persistent volume ==="
fly volumes create sentinelx_data --size 1 --region hkg 2>/dev/null || echo "Volume already exists"

echo "=== 4. Setting secrets ==="
if [ "$ENCRYPTION_KEY" = "change_me_to_64_hex_chars_from_os_urandom_32" ]; then
    ENCRYPTION_KEY=$(python -c "import os; print(os.urandom(32).hex())")
    echo "Generated new ENCRYPTION_KEY"
fi
fly secrets set ENCRYPTION_KEY="$ENCRYPTION_KEY" 2>/dev/null || true
fly secrets set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" 2>/dev/null || true
fly secrets set JWT_SECRET="$JWT_SECRET" 2>/dev/null || true

echo "=== 5. Deploying ==="
fly deploy

echo ""
echo "=== Deploy Complete ==="
echo "App URL: https://sentinelx-mvp.fly.dev"
echo "Health:  curl https://sentinelx-mvp.fly.dev/health"
echo ""
echo "Next: Deploy Telegram Bot to Cloudflare Workers:"
echo "  cd bot && wrangler deploy"
