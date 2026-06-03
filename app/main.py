"""SentinelX MVP - FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from jinja2 import Environment, FileSystemLoader

from app.config import settings

# Templates (for web pages)
templates_dir = Path(__file__).parent / "web" / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    import sys, traceback
    print(f"[SentinelX] Starting {settings.APP_NAME} v{settings.APP_VERSION}", flush=True)
    print(f"[SentinelX] Debug mode: {settings.DEBUG}", flush=True)

    try:
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(exist_ok=True)

        from app.core.database import init_db
        await init_db()
        print("[SentinelX] Database initialized", flush=True)

        from app.engine.data_feed import data_feed
        data_feed.start()
        print("[SentinelX] DataFeed started", flush=True)
    except Exception as e:
        print(f"[SentinelX] STARTUP ERROR: {e}", flush=True)
        traceback.print_exc(file=sys.stderr)
        raise

    yield

    data_feed.stop()
    print("[SentinelX] Shutting down...", flush=True)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Register routers
from app.web.routes import router as web_router
from app.api.v1.auth import router as auth_router
from app.api.v1.wallets import router as wallet_router
from app.api.v1.bot_integration import router as bot_router
from app.api.v1.markets import router as markets_router
from app.api.v1.trades import router as trades_router
from app.api.v1.copy_trades import router as copy_router
from app.api.v1.security_api import router as security_router
from app.api.v1.settings import router as settings_router

app.include_router(web_router, tags=["web"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(wallet_router, prefix="/api/v1/wallet", tags=["wallet"])
app.include_router(bot_router, prefix="/api/v1/bot", tags=["bot"])
app.include_router(markets_router, prefix="/api/v1/markets", tags=["markets"])
app.include_router(trades_router, prefix="/api/v1/trades", tags=["trades"])
app.include_router(copy_router, prefix="/api/v1/copy", tags=["copy"])
app.include_router(security_router, prefix="/api/v1/security", tags=["security"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["settings"])


# ---- Health Check ----
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.APP_VERSION}


# ---- Root / Web Pages ----
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Home page."""
    template = jinja_env.get_template("index.html")
    return HTMLResponse(
        template.render(
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
        )
    )


# ---- Run ----
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
