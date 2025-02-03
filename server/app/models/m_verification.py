import uuid
from datetime import datetime, timedelta
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship, deferred
from sqlalchemy import String, ForeignKey, DateTime, Enum, Text, UUID
from config.database import Base
from config.settings import DEFAULT_TIMEZONE

class VerificationStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class IdentityVerification(Base):
    __tablename__ = "identity_verifications"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    encrypted_id_card_mrz: Mapped[str] = deferred(mapped_column(Text, nullable=False))
    
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[str] = mapped_column(String(10), nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    
    status: Mapped[VerificationStatus] = mapped_column(Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(DEFAULT_TIMEZONE), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(DEFAULT_TIMEZONE) + timedelta(days=730), nullable=False)
    
    user = relationship("User", back_populates="identity_verifications")
