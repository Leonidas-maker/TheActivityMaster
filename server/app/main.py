from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from config.database import engine, Base

from models.generic import *
from models.user import *
from models.club import *
from models.audit import *

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)