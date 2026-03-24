import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from shared.core.database import Base


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_users_email", "email"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
