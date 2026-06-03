"""Web page routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import settings

router = APIRouter(prefix="/web")
jinja_env = None  # Will be set from main.py


def get_jinja():
    """Lazy import to avoid circular imports."""
    from app.main import jinja_env as env
    return env


@router.get("/", response_class=HTMLResponse)
async def web_index(request: Request):
    """Web home page."""
    return HTMLResponse(
        get_jinja().get_template("index.html").render(
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
        )
    )


@router.get("/wallet/bind", response_class=HTMLResponse)
async def wallet_bind_page(request: Request):
    """Wallet binding page."""
    return HTMLResponse(
        get_jinja().get_template("wallet_bind.html").render()
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """User dashboard page."""
    return HTMLResponse(
        get_jinja().get_template("dashboard.html").render(
            wallet=None,
            wallet_address="N/A",
            wallet_label="N/A",
            usdc_balance=0.0,
            matic_balance=0.0,
            total_trades=0,
            total_pnl=0.0,
            win_rate=0.0,
        )
    )
