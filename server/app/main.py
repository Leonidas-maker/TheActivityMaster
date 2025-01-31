from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import engine, get_async_session, get_db, check_db_connection
from config.settings import ENVIRONMENT
from config.database import Base
from core.init_database import init_country_states_city, init_country_states_city_mode, init_users

from models.m_generic import *
from models.m_user import *
from models.m_club import *
from models.m_audit import *
from models.m_payment import *

import schemas.s_generic as s_generic
from crud import generic as crud_generic

from core.security import jwt_key_manager_dependency, totp_manager_dependency, email_verify_manager_dependency

from utils.jwt_keyfile_manager import JWTKeyManager
from utils.totp_manager import TOTPManager
from utils.email_verify_manager import EmailVerifyManager

from api.v1.router import router as v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_connection(engine)
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with get_async_session() as db:
        await init_users(db)
        await init_country_states_city(db, mode=init_country_states_city_mode.country)

    # Initialize the JWT key manager 
    km = JWTKeyManager()
    jwt_key_manager_dependency.init(km)

    # Initialize the TOTP manager
    totp_m = TOTPManager()
    totp_manager_dependency.init(totp_m)

    # Initialize the Email Verify manager
    evm = EmailVerifyManager()
    email_verify_manager_dependency.init(evm)

    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(v1_router, prefix="/api/v1")

@app.get("/ping")
def read_root():
    return {"message": "pong"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
