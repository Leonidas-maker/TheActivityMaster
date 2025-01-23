from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from schemas.s_user import UserCreate

from controllers.user import register_user

# Router for user endpoints
router = APIRouter()

@router.post("/register")
async def register_user_v1(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user
    """
    try:
        user_id = await register_user(db, user)
        return {"message": "User registered", "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid user data")