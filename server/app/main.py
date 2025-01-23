from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import engine, Base, get_async_session, get_db, check_db_connection
from config.settings import ENVIRONMENT
from core.init_database import init_country_states_city, init_country_states_city_mode, init_users

from models.m_generic import *
from models.m_user import *
from models.m_club import *
from models.m_audit import *
from models.m_payment import *

import schemas.s_generic as s_generic
from crud import generic as crud_generic
import utils.jwt_keyfiles as jwt_keyfiles

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

    jwt_keyfiles.generate_keys()

    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(v1_router, prefix="/api/v1")

@app.get("/ping")
def read_root():
    return {"message": "pong"}


@app.post("/address", response_model=s_generic.Address)
async def create_address(address: s_generic.Address, db: AsyncSession = Depends(get_db)):
    try:
        address = await crud_generic.get_create_address(db, address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid country")
    return s_generic.Address(
        street=address.street,
        postal_code=address.postal_code.code,
        city=address.postal_code.city.name,
        state=address.postal_code.city.state.name,
        country=address.postal_code.city.state.country.name,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
