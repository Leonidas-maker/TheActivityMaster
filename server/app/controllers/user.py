from sys import audit
from turtle import st
from fastapi import HTTPException
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import traceback

from models.m_user import User

from schemas.s_user import UserCreate

from core.security import hash_password

from crud.audit import AuditLogger
from crud.user import create_user
import time


async def register_user(db: AsyncSession, user: UserCreate) -> uuid.UUID:
    """
    Register a new user

    :param db: The database session
    :param username: The username of the new user
    :param password: The password of the new user
    :return: The user ID of the new user
    """
    
    # Check if the user already exists
    res = await db.execute(select(User).filter(User.email == user.email))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Add audit logs
    audit_logger = AuditLogger(db)
    audit_logger.sys_info("Registering a new user")

    try:
        # Hash the password
        user.password = hash_password(user.password)

        # Create the user
        user_db = await create_user(db, user)
        user_id = user_db.id 

        # Add audit logs
        audit_logger.sys_info("User registered", details=f"User ID: {user_id}")
        await db.commit()

        return user_id
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid user data: {ve}")
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error("Failed to register a new user", traceback=traceback.format_exc())
        await db.commit()
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to register user. Please try again later.")
