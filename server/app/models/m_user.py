from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship, deferred
from sqlalchemy import (
    TIMESTAMP,
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
    UUID,
    Boolean,
    DateTime,
    Enum,
    Text,
    Index,
)
from sqlalchemy.ext.associationproxy import association_proxy
import uuid
from datetime import datetime
import enum
from typing import Dict

from config.database import Base
from config.settings import DEFAULT_TIMEZONE

from models.m_generic import *
from models.m_club import *
from models.m_audit import *
from models.m_payment import *
from models.m_verification import IdentityVerification


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    address_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True)

    backup_codes_2fa: Mapped[str] = deferred(mapped_column(String(1000), nullable=True))  # Backup codes for 2FA
    is_newsletter_subscribed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_passkey_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    is_anonymized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    address: Mapped["Address"] = relationship("Address")
    identity_verifications: Mapped[List["IdentityVerification"]] = relationship("IdentityVerification", uselist=True)
    generic_roles: Mapped[List["GenericRole"]] = relationship(
        "GenericRole", secondary="user_roles", uselist=True, back_populates="users", lazy="joined"
    )
    club_roles: Mapped[List["UserClubRole"]] = relationship("UserClubRole", back_populates="user", uselist=True)
    
    #roles = association_proxy("club_roles", "club_role")

    tokens: Mapped[List["UserToken"]] = relationship(
        "UserToken", back_populates="user", uselist=True, cascade="all, delete-orphan"
    )
    passkeys: Mapped[List["UserPasskey"]] = relationship("UserPasskey", back_populates="user", uselist=True)
    _2fa: Mapped[List["User2FA"]] = relationship("User2FA", back_populates="user", uselist=True)

    membership_subscriptions: Mapped[List["MembershipSubscription"]] = relationship(
        "MembershipSubscription", back_populates="user", uselist=True
    )
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="user", uselist=True)
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="user", uselist=True)

    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", uselist=True)
    authentication_logs: Mapped[List["AuthenticationLog"]] = relationship(
        "AuthenticationLog", back_populates="user", uselist=True
    )

    @property
    def clubs_with_roles(self) -> Dict[uuid.UUID, "ClubRole"]:
        result = {}
        for ucr in self.club_roles:
            result[ucr.club_id] = ucr.club_role
        return result


class GenericRole(Base):
    __tablename__ = "generic_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = deferred(mapped_column(String(255), nullable=False))

    users: Mapped[List["User"]] = relationship(
        "User", secondary="user_roles", uselist=True, back_populates="generic_roles"
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("generic_roles.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="unique_user_role"),)


class User2FAMethods(enum.Enum):
    EMAIL = "email"
    TOTP = "totp"


class User2FA(Base):
    """
    User 2FA table

    ## Wichtige Felder, die doppelt vergeben werden:
    :param public_key: str: Der Public Key für die 2FA-Methode
    :param key_handle: str: Secret key für TOTP | Key handle für U2F
    :param counter: int: Letzter verwendeter Counter für TOTP oder U2F
    :param device_name: str: Name des Geräts
    """

    __tablename__ = "user_2fa"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    method: Mapped[User2FAMethods] = mapped_column(Enum(User2FAMethods), nullable=False)

    public_key: Mapped[str] = mapped_column(String(512), nullable=True)  # Public key wie bei U2F
    key_handle: Mapped[str] = mapped_column(String(255), nullable=True)  # Secret key für TOTP | Key handle für U2F
    counter: Mapped[int] = mapped_column(Integer, nullable=True)  # Letzter verwendeter Counter für TOTP oder U2F
    fails: Mapped[int] = mapped_column(
        Integer, nullable=False, default=-1
    )  # Anzahl fehlgeschlagener Versuche; -1 wenn die Methode nicht validiert ist
    device_name: Mapped[str] = mapped_column(String(100), nullable=True)  # Name des Geräts

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    user: Mapped["User"] = relationship("User", back_populates="_2fa")


class UserPasskey(Base):
    __tablename__ = "user_passkeys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    credential_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  # Generiert durch WebAuthn
    public_key: Mapped[str] = mapped_column(
        Text(1000), nullable=False
    )  # Öffentlicher Schlüssel, generiert durch WebAuthn
    sign_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )  # Counter zum Verhindern von Replay-Attacken
    device_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Name des Geräts
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    user: Mapped["User"] = relationship("User", back_populates="passkeys")


class TokenTypes(enum.Enum):
    REFRESH = "refresh"
    ACCESS = "access"
    SECURITY = "security"


class UserToken(Base):
    __tablename__ = "user_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    application_id_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    token_type: Mapped[TokenTypes] = mapped_column(Enum(TokenTypes), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="tokens")

    __table_args__ = (Index("ix_user_tokens_user_id", "user_id"),)
