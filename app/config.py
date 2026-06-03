"""SentinelX MVP - Application Configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment."""

    # App
    APP_NAME: str = os.getenv("APP_NAME", "SentinelX MVP")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///data/sentinelx.db"
    )

    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "0" * 64)

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Polymarket
    POLYMARKET_API_KEY: str = os.getenv("POLYMARKET_API_KEY", "")
    POLYMARKET_API_SECRET: str = os.getenv("POLYMARKET_API_SECRET", "")
    POLYMARKET_API_PASSPHRASE: str = os.getenv("POLYMARKET_API_PASSPHRASE", "")

    # Polygon
    RPC_URL: str = os.getenv("RPC_URL", "https://polygon-rpc.com")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "137"))

    # Web
    WEB_APP_URL: str = os.getenv("WEB_APP_URL", "http://localhost:8000")

    # Deployment (Railway sets PORT automatically)
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")


settings = Settings()
