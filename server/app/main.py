from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from core.database import engine, get_async_session, check_db_connection
from config.settings import ENVIRONMENT
from config.database import Base
from core.init_database import init_country_states_city, init_country_states_city_mode, init_users

from models.m_generic import *
from models.m_user import *
from models.m_club import *
from models.m_audit import *
from models.m_payment import *

from core.security import (
    jwt_key_manager_dependency,
    totp_manager_dependency,
    email_verify_manager_dependency,
    ec_encryptor_dependency,
)

from crud.audit import anonymize_ip_addresses
from crud.auth import clean_tokens, totp_key_rotation
from crud.verification import delete_expired_identity_verifications

from utils.jwt_keyfile_manager import JWTKeyManager
from utils.totp_manager import TOTPManager
from utils.email_verify_manager import EmailVerifyManager
from utils.asymmetric_ev_encryptor import AsymmetricECEncryptor
from utils.task_scheduler import TaskSchedulerRedis

from api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_connection(engine)
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
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

    # Initialize the EC Encryptor
    ec_encryptor = AsymmetricECEncryptor()
    ec_encryptor_dependency.init(ec_encryptor)
     
    # Initialize the Task Scheduler
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    scheduler = TaskSchedulerRedis(redis_host=redis_host)

    # Clean up the audit logs
    scheduler.add_task(
        "anonymize_ip_addresses", anonymize_ip_addresses, cron="0 0 * * *", on_startup=True, with_console=True
    )

    # Clean up the tokens
    scheduler.add_task("clean_tokens", clean_tokens, cron="0 * * * *", on_startup=True, with_console=True)

    # Rotate the TOTP keys every 14 days
    scheduler.add_task("totp_key_rotation", totp_key_rotation, cron="0 0 */14 * *", on_startup=True, with_console=True)

    # Delete expired identity verifications every 7 days
    scheduler.add_task(
        "delete_expired_identity_verifications",
        delete_expired_identity_verifications,
        cron="0 0 */7 * *",
        on_startup=True,
        with_console=True,
    )

    scheduler.start()
    yield
    scheduler.stop()
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"operationsSorter": "tag"},
    title="🏃‍♂️ TheActivityMaster API",
    version="0.0.2",
    contact={
        "name": "TheActivityMaster Support",
    },
)

app.include_router(v1_router, prefix="/api/v1")
static_folder = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_folder), name="static")


@app.get("/ping")
def read_root():
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
