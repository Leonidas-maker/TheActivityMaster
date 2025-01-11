from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, UUID, Boolean, DateTime, PrimaryKeyConstraint, Enum, Text, DECIMAL, Time
import uuid
from datetime import datetime, time
import enum

from models.user import *
from config.database import Base
from config.settings import DEFAULT_TIMEZONE

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    action: Mapped[Annotated[Text, mapped_column(Text, nullable=False)]]
    timestamp: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]

    user = relationship("User", back_populates="audit_logs")

class AuthMethods(enum.Enum):
    PASSWORD = "password"
    PASSKEY = "passkey"
    EMAIL = "email"
    TOTP = "totp"

class AuthenticationLog(Base):
    __tablename__ = "authentication_logs"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    method: Mapped[Annotated[AuthMethods, mapped_column(Enum(AuthMethods), nullable=False)]]
    ip_address: Mapped[Annotated[Text, mapped_column(Text, nullable=False)]]
    status: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False)]]
    timestamp: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]