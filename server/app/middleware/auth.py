from fastapi import Depends, HTTPException, status, Header, Request, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import time

from config.permissions import ClubPermissions
from core.database import get_db

from crud import auth as auth_crud, user as user_crud, role as role_crud

from core.security import TokenDetails

from models.m_user import TokenTypes

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

roles_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient permissions",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AccessTokenChecker:
    def __init__(self, generic_roles: Optional[list[str]] = None, club_permissions: Optional[list[ClubPermissions]] = None):
        """
        :param generic_roles: Legacy generic roles that are required will be migrated to permissions in the future, defaults to None
        :param club_permissions: Club permissions that are required, defaults to None
        """

        self.generic_roles = [generic_role.lower() for generic_role in generic_roles] if generic_roles else None
        self.club_permissions = club_permissions

    async def __call__(
        self,
        request: Request,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme),
        application_id: str = Header(...),
    ) -> TokenDetails:
        # Check Token
        if not application_id:
            raise HTTPException(status_code=401, detail="Invalid application ID")

        payload = await auth_crud.verify_token(db, token, TokenTypes.ACCESS, application_id)
        if not payload:
            raise credentials_exception

        user_id = uuid.UUID(payload["sub"])

        # Check Generic Roles
        if self.generic_roles:
            if not await role_crud.has_user_any_generic_role(db, user_id, self.generic_roles):
                raise roles_exception
            return TokenDetails(payload=payload, application_id=application_id, user_id=user_id)
        
        # Check Club Permissions
        if self.club_permissions:
            try:
                club_id = uuid.UUID(request.path_params["club_id"])
            except Exception:
                raise HTTPException(status_code=400, detail="A valid Club-ID is required")

            if not await role_crud.has_user_any_club_permission(db, user_id, club_id, self.club_permissions):
                raise roles_exception
        return TokenDetails(payload=payload, application_id=application_id, user_id=user_id)


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
    return TokenDetails(payload=payload, application_id=application_id, user_id=uuid.UUID(payload["sub"]))


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

        payload = await auth_crud.verify_token(db, token, TokenTypes.SECURITY, application_id)
        if not payload:
            raise credentials_exception

        if self.amr not in payload["amr"]:
            raise credentials_exception

        return TokenDetails(payload=payload, application_id=application_id, user_id=uuid.UUID(payload["sub"]))
