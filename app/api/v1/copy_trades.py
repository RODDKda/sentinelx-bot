"""Copy Trade API routes."""

from fastapi import APIRouter
from app.engine.copy_manager import copy_manager

router = APIRouter()


@router.post("/start")
async def start_copying(
    follower_id: str,
    leader_id: str,
    max_per_trade: float = 100.0,
    total_cap: float = 1000.0,
    copy_ratio: float = 1.0,
):
    """Start copying a leader."""
    result = copy_manager.start_copying(
        follower_id=follower_id,
        leader_id=leader_id,
        max_per_trade=max_per_trade,
        total_cap=total_cap,
        copy_ratio=copy_ratio,
    )
    return result


@router.post("/stop")
async def stop_copying(follower_id: str, leader_id: str):
    """Stop copying a leader."""
    return copy_manager.stop_copying(follower_id, leader_id)


@router.get("/following")
async def get_following(follower_id: str):
    """Get all leaders a user follows."""
    return {"following": copy_manager.get_following(follower_id)}


@router.get("/followers")
async def get_followers(leader_id: str):
    """Get all followers of a leader."""
    return {"followers": copy_manager.get_followers(leader_id)}


@router.get("/history")
async def get_copy_history(follower_id: str = ""):
    """Get copy trade history."""
    return {"trades": copy_manager.get_copy_trade_history(follower_id or None)}


@router.get("/stats")
async def get_leader_stats(leader_id: str):
    """Get leader stats."""
    return copy_manager.get_leader_stats(leader_id)
