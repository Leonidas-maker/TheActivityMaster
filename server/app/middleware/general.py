from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.generic import EndpointContext

from crud.audit import AuditLogger

async def get_endpoint_context(
    db: AsyncSession = Depends(get_db),
) -> EndpointContext:
    """Get the endpoint context"""
    audit_logger = AuditLogger(db)
    return EndpointContext(db=db, audit_logger=audit_logger)