from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from rich.console import Console
from rich.style import Style

from core.database import engine, get_async_session, check_db_connection, get_db
from config.settings import ENVIRONMENT
from config.database import Base
import core.init_database as init_db

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
from crud.auth import clean_tokens, totp_key_rotation, clean_2fa_table
from crud.verification import delete_expired_identity_verifications
from crud.club import (
    update_session_occurrences,
    refresh_bookings_status,
    set_programs_inactive,
    delete_marked_clubs,
    cancel_bookings_for_cancelled_membership_subscriptions,
)
from crud.transactions import check_pending_transactions

from utils.jwt_keyfile_manager import JWTKeyManager
from utils.totp_manager import TOTPManager
from utils.email_verify_manager import EmailVerifyManager
from utils.asymmetric_ev_encryptor import AsymmetricECEncryptor
from utils.task_scheduler import TaskSchedulerRedis

from api.v1.router import router as v1_router

banner = """                                                                                                                                                                                                                                                                                         
.------------------------------------------------.
|       🏃͋̔͊‍̾̔͊♂͒̒͘️̒͊͝ T̕͝͠h̾̀̕e̾͑̾A͋͠c̔͆̒t͆̀͝i̐͆v̽́i̒͘͘t̀̚͠y͛̽M͋̚a̿͒s̓́͒t̓̈́e͋̈́̽r͛̚ -̔͒ B̓̕͠a̐͐͝c̓̈́͠k͊̔͝e̾͐͠n̈́͌͋d̾̈́̾          |
'------------------------------------------------'
                   .-~~~~-.
                 .'        '.
                /            \\
               /              \\
              |   ( )    ( )   |
              |       ^^       |
              |   \\   __   /   |
              |    \\      /    |
              \\     \\____/     /
               \\              /
                 '.         .'
                   '-.~~.-'

"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    console = Console()
    style = Style(color="red", bold=True)
    console.print(banner, style=style)

    await check_db_connection(engine)

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with get_async_session() as db:
        await init_db.init_users(db)
        await init_db.init_country_states_city(db, mode=init_db.init_country_states_city_mode.country)
        await init_db.init_program_categories(db)

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

    # Initialize the Redis connection
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port = os.getenv("REDIS_PASSWORD", "root")

    # Initialize the FastAPI Cache
    redis = aioredis.Redis(host=redis_host, db=0, password=redis_port)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    # Initialize the Task Scheduler
    scheduler = TaskSchedulerRedis(redis_host=redis_host, redis_password=redis_port, redis_db=1)

    # Clean up the audit logs
    scheduler.add_task(
        "anonymize_ip_addresses", anonymize_ip_addresses, cron="0 0 * * *", on_startup=True, with_console=True
    )

    # Clean up the tokens
    scheduler.add_task("clean_tokens", clean_tokens, cron="0 * * * *", on_startup=True, with_console=True)

    # Rotate the TOTP keys every 14 days
    scheduler.add_task("totp_key_rotation", totp_key_rotation, cron="0 0 */14 * *", on_startup=True, with_console=True)

    # Clean up the 2fa table
    scheduler.add_task(
        "clean_2fa",
        clean_2fa_table,
        cron="*/15 * * * *",
        on_startup=True,
        with_console=True,
        blocked_by=["totp_key_rotation"],
    )

    # Delete expired identity verifications every 7 days
    scheduler.add_task(
        "delete_expired_identity_verifications",
        delete_expired_identity_verifications,
        cron="0 0 */7 * *",
        on_startup=True,
        with_console=True,
    )

    # Update the session occurrences daily
    scheduler.add_task(
        "update_session_occurrences",
        update_session_occurrences,
        cron="0 0 * * *",
        on_startup=True,
        with_console=True,
    )

    # Delete clubs that are marked for deletion every week
    scheduler.add_task(
        "delete_marked_clubs",
        delete_marked_clubs,
        cron="0 0 * * 0",
        with_console=True,
    )

    # Update program status to inactive if the end date is passed
    scheduler.add_task(
        "set_programs_inactive",
        set_programs_inactive,
        cron="0 0 * * *",
        on_startup=True,
        with_console=True,
        blocked_by=["delete_marked_clubs"],
    )

    # Cancel bookings for cancelled membership subscriptions
    scheduler.add_task(
        "cancel_bookings_for_cancelled_membership_subscriptions",
        cancel_bookings_for_cancelled_membership_subscriptions,
        cron="0 0 * * *",
        on_startup=True,
        with_console=True,
    )

    # Refresh the bookings status every 15 minutes
    scheduler.add_task(
        "refresh_bookings_status",
        refresh_bookings_status,
        cron="*/15 * * * *",
        on_startup=True,
        with_console=True,
        blocked_by=["cancel_bookings_for_cancelled_membership_subscriptions"],
    )

    # Check pending transactions every 5 minutes
    scheduler.add_task(
        "check_pending_transactions",
        check_pending_transactions,  #! Dummy function is used for now
        cron="*/5 * * * *",
        on_startup=True,
        with_console=True,
    )

    scheduler.start()
    yield
    scheduler.stop()
    await engine.dispose()

tags_metadata = [
    {
        "name": "Access: Public",
        "description": "Public endpoints doesn't require authentication.",
    },
    {
        "name": "Access: Hybrid",
        "description": """Hybrid endpoints doesn't require authentication 
                but the response is different based on the user's permissions. **See the notes in the endpoints for more details.**""",
    },
]

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"operationsSorter": "tag"},
    title="🏃‍♂️ TheActivityMaster API",
    version="0.0.2",
    contact={
        "name": "TheActivityMaster Support",
    },
    openapi_tags=tags_metadata,
)

app.include_router(v1_router, prefix="/api/v1")
static_folder = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_folder), name="static")


@app.get("/ping")
def ping():
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
