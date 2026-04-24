"""
Usage limit manager for FiiLTHY SaaS.
Handles plan limits, usage tracking, and plan upgrades.
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException

# Plan limits: -1 means unlimited
PLAN_LIMITS = {
    "free": 5,
    "starter": 50,
    "pro": 500,
    "enterprise": -1,  # unlimited
}

# Stripe subscription price IDs (set via environment variables)
PLAN_PRICE_IDS = {
    "starter": os.environ.get("STRIPE_PRICE_STARTER", ""),
    "pro": os.environ.get("STRIPE_PRICE_PRO", ""),
    "enterprise": os.environ.get("STRIPE_PRICE_ENTERPRISE", ""),
}

PLAN_NAMES = {
    "free": "Free",
    "starter": "Starter",
    "pro": "Pro",
    "enterprise": "Enterprise",
}

PLAN_PRICES = {
    "starter": 2900,   # $29.00 in cents
    "pro": 7900,       # $79.00 in cents
    "enterprise": 29900,  # $299.00 in cents
}


async def get_user_usage(user_id: str, db) -> Dict[str, Any]:
    """Get current plan and usage stats for a user."""
    if db is None:
        # Fallback when DB is unavailable
        return {
            "plan": "free",
            "generations_used": 0,
            "limit": PLAN_LIMITS["free"],
            "remaining": PLAN_LIMITS["free"],
            "unlimited": False,
        }

    users_collection = db["users"]
    user = await users_collection.find_one({"id": user_id}, {"_id": 0})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = user.get("plan", "free")
    generations_used = user.get("generations_used", 0)
    limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    unlimited = limit == -1
    remaining = "unlimited" if unlimited else max(0, limit - generations_used)

    return {
        "plan": plan,
        "plan_name": PLAN_NAMES.get(plan, plan.capitalize()),
        "generations_used": generations_used,
        "limit": limit,
        "remaining": remaining,
        "unlimited": unlimited,
    }


async def check_and_increment_usage(user_id: str, db) -> Dict[str, Any]:
    """
    Check if user has remaining generations and increment by 1.
    Raises HTTPException with LIMIT_REACHED if exceeded.
    Returns updated usage stats on success.
    """
    usage = await get_user_usage(user_id, db)

    if not usage["unlimited"] and usage["generations_used"] >= usage["limit"]:
        raise HTTPException(
            status_code=403,
            detail="LIMIT_REACHED"
        )

    if db is not None:
        users_collection = db["users"]
        await users_collection.update_one(
            {"id": user_id},
            {"$inc": {"generations_used": 1}}
        )

    usage["generations_used"] += 1
    if not usage["unlimited"]:
        usage["remaining"] = max(0, usage["limit"] - usage["generations_used"])

    return usage


async def reset_usage(user_id: str, db) -> None:
    """Reset generations_used to 0 (e.g., after plan upgrade or billing cycle)."""
    if db is None:
        return
    users_collection = db["users"]
    await users_collection.update_one(
        {"id": user_id},
        {"$set": {"generations_used": 0, "updated_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc)}}
    )


async def update_user_plan(user_id: str, plan: str, db) -> Dict[str, Any]:
    """Update user plan and reset usage."""
    if plan not in PLAN_LIMITS:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    users_collection = db["users"]
    result = await users_collection.update_one(
        {"id": user_id},
        {
            "$set": {
                "plan": plan,
                "generations_used": 0,
                "updated_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "plan": plan,
        "limit": PLAN_LIMITS[plan],
        "message": f"Plan updated to {PLAN_NAMES.get(plan, plan)}"
    }


async def get_or_create_user_by_id(user_id: str, db) -> Dict[str, Any]:
    """
    Get user by id; if not found, create a free-tier user.
    Used for lightweight user system (e.g., localStorage user_id).
    """
    if db is None:
        return {
            "id": user_id,
            "plan": "free",
            "generations_used": 0,
        }

    users_collection = db["users"]
    user = await users_collection.find_one({"id": user_id}, {"_id": 0})

    if not user:
        # Create lightweight user
        user = {
            "id": user_id,
            "plan": "free",
            "generations_used": 0,
            "created_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
            "updated_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
        }
        await users_collection.insert_one(user)

    return user

