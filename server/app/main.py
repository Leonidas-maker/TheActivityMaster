from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import uvicorn

from config.database import engine, Base, get_async_session, get_db
from config.init_database import init_country_states_city

from models.m_generic import *
from models.m_user import *
from models.m_club import *
from models.m_audit import *

import schemas.s_generic as s_generic
from sqlalchemy.ext.asyncio import AsyncSession
from crud import generic as crud_generic

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with get_async_session() as db:
        await init_country_states_city(db)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/ping")
def read_root():
    return {"message": "pong"}

@app.post("/address")
async def create_address(address: s_generic.Address, db: AsyncSession = Depends(get_db)):
    address = await crud_generic.create_address(db, address)
    return address

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)