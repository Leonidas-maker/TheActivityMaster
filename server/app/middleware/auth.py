from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from crud import auth as auth_crud

from core.security import TokenDetails

from models.m_user import TokenTypes

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def check_access_token(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    application_id: str = Header(...),
) -> TokenDetails:
    if not application_id:
        raise HTTPException(status_code=401, detail="Invalid application ID")

    payload = await auth_crud.verify_token(db, token, TokenTypes.ACCESS, application_id)
    if not payload:
        raise credentials_exception
    return TokenDetails(payload=payload, application_id=application_id)

async def check_refresh_token(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    application_id: str = Header(...),
) -> TokenDetails:
    if not application_id:
        raise HTTPException(status_code=401, detail="Invalid application ID")

    payload = await auth_crud.verify_token(db, token, TokenTypes.REFRESH, application_id)
    if not payload:
        raise credentials_exception
    return TokenDetails(payload=payload, application_id=application_id)

class SecurityTokenChecker:
    def __init__(self, amr: str):
        self.amr = amr

    async def __call__(
        self,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme),
        application_id: str = Header(...),
    ) -> TokenDetails:
        if not application_id:
            raise HTTPException(status_code=401, detail="Invalid application ID")

        payload = await auth_crud.verify_token(
            db, token, TokenTypes.SECURITY, application_id
        )
        if not payload:
            raise credentials_exception

        if self.amr not in payload["amr"]:
            raise credentials_exception

        return TokenDetails(payload=payload, application_id=application_id)