from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event
import os
from contextlib import asynccontextmanager

from config.settings import DEFAULT_TIMEZONE


# Database Path
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "root:root@127.0.0.1:3306/tam"

###########################################################################
############################ Async for FastAPI ############################
###########################################################################
engine = create_async_engine(f"mysql+asyncmy://{SQLALCHEMY_DATABASE_URL}")
@event.listens_for(engine.sync_engine, "connect")
def set_session_timezone(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(f"SET time_zone = '{DEFAULT_TIMEZONE.zone}'")
    cursor.close()

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, future=True)
Base = declarative_base()

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

@asynccontextmanager
async def get_async_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()