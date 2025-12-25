"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional

from app.core.supabase import verify_jwt_token
from app.models import UserInfo


router = APIRouter()


async def get_current_user(authorization: Optional[str] = Header(None)) -> UserInfo:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        UserInfo with user details
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
        )
    
    token = parts[1]
    user_data = await verify_jwt_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )
    
    return UserInfo(
        id=user_data["id"],
        email=user_data.get("email"),
        name=user_data.get("user_metadata", {}).get("full_name"),
        avatar_url=user_data.get("user_metadata", {}).get("avatar_url"),
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/verify")
async def verify_token(current_user: UserInfo = Depends(get_current_user)):
    """Verify if the current token is valid."""
    return {"valid": True, "user_id": current_user.id}

