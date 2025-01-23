from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UUID, Boolean, DateTime, Enum, Text
import uuid
from datetime import datetime
import enum

from .m_user import *
from config.database import Base
from config.settings import DEFAULT_TIMEZONE

class AuditLogCategories(enum.Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    CLUB = "CLUB"
    PAYMENT = "PAYMENT"
    GENERIC = "GENERIC"

class AuditLog(Base):
    __tablename__ = "logs_audit"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    action: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]
    category: Mapped[Annotated[AuditLogCategories, mapped_column(Enum(AuditLogCategories), nullable=False)]]
    timestamp: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]]
    status: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False, default=True)]]
    details: Mapped[Annotated[str, mapped_column(Text, nullable=True)]] 

    user: Mapped["User"] = relationship("User", back_populates="audit_logs")

class AuthMethods(enum.Enum):
    PASSWORD = "password"
    PASSKEY = "passkey"
    EMAIL = "email"
    TOTP = "totp"
    U2F = "u2f"
    TOKEN_CREATE = "token_create"
    TOKEN_REFRESH = "token_refresh"

class AuthenticationLog(Base):
    __tablename__ = "logs_authentication"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    method: Mapped[Annotated[AuthMethods, mapped_column(Enum(AuthMethods), nullable=False)]]
    timestamp: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]]

    ip_address: Mapped[Annotated[Text, mapped_column(Text, nullable=False)]]
    status: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False)]]
    details: Mapped[Annotated[str, mapped_column(Text, nullable=True)]] 
    

    user: Mapped["User"] = relationship("User", back_populates="authentication_logs")

class ErrorLevels(enum.Enum):
    DEBUG = "DEBUG"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorLog(Base):
    __tablename__ = "logs_error"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    timestamp: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]]
    level: Mapped[Annotated[ErrorLevels, mapped_column(Enum(ErrorLevels), nullable=False)]]
    message: Mapped[Annotated[str, mapped_column(Text, nullable=False)]]
    traceback: Mapped[Annotated[str, mapped_column(Text, nullable=True)]]
    correlation_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), nullable=True)]]
 