from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, UUID, Boolean, DateTime, PrimaryKeyConstraint, Enum, Text
import uuid
from datetime import datetime
import enum
from typing import List

from models.m_generic import *
from models.m_club import *
from models.m_audit import *
from config.database import Base
from config.settings import DEFAULT_TIMEZONE

class User(Base):
    __tablename__ = "users"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    first_name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    last_name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    email: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]
    password: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]

    address_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)]]
    is_2fa_enabled: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False, default=False)]]
    is_passkey_enabled: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False, default=False)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    address: Mapped["Address"] = relationship("Address")
    generic_roles: Mapped[List["GenericRole"]] = relationship(
        "GenericRole", 
        secondary="user_roles", 
        uselist=True, 
        back_populates="users"
    )
    club_roles: Mapped[List["ClubRole"]] = relationship(
        "ClubRole", 
        secondary="user_club_roles", 
        uselist=True, 
        back_populates="users"
    )
    tokens: Mapped[List["UserToken"]] = relationship("UserToken", back_populates="user")
    passkeys: Mapped[List["UserPasskey"]] = relationship("UserPasskey", back_populates="user", uselist=True)
    _2fa: Mapped[List["User2FA"]] = relationship("User2FA", back_populates="user", uselist=True)

    membership_subscriptions: Mapped[List["MembershipSubscription"]] = relationship(
        "MembershipSubscription", 
        back_populates="user", 
        uselist=True
    )
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="user", uselist=True)
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="user", uselist=True)

    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", uselist=True)
    authentication_logs: Mapped[List["AuthenticationLog"]] = relationship(
        "AuthenticationLog", 
        back_populates="user", 
        uselist=True
    )


class GenericRole(Base):
    __tablename__ = "generic_roles"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]
    
    users: Mapped[List["User"]] = relationship("User", secondary="user_roles", uselist=True, back_populates="generic_roles")

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)]]
    role_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("generic_roles.id"), primary_key=True)]]
    assigned_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="unique_user_role"),)

class User2FAMethods(enum.Enum):
    EMAIL = "email"
    TOTP = "totp"

class User2FA(Base):
    __tablename__ = "user_2fa"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    method: Mapped[Annotated[User2FAMethods, mapped_column(Enum(User2FAMethods), nullable=False)]] 
    secret: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]
    last_code: Mapped[Annotated[str, mapped_column(String(20), nullable=True)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    user: Mapped["User"] = relationship("User", back_populates="_2fa")


class UserPasskey(Base):
    __tablename__ = "user_passkeys"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    credential_id: Mapped[Annotated[str, mapped_column(String(255), nullable=False, unique=True)]] # Generated by WebAuthn
    public_key: Mapped[Annotated[str, mapped_column(Text(1000), nullable=False)]] # Public key generated by WebAuthn
    sign_count: Mapped[Annotated[int, mapped_column(Integer, nullable=False, default=0)]] # Counter to prevent replay attacks
    device_name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]] # Name of the device
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    user: Mapped["User"] = relationship("User", back_populates="passkeys")

class TokenTypes(enum.Enum):
    REFRESH = "refresh"
    ACCESS = "access"
    SECURITY = "security"

class UserToken(Base):
    __tablename__ = "user_tokens"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    token_type: Mapped[Annotated[TokenTypes, mapped_column(Enum(TokenTypes), nullable=False)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    
    user: Mapped["User"] = relationship("User", back_populates="tokens")