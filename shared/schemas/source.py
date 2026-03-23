from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Dict, Any


class SourceUIConfig(BaseModel):
    """UI configuration for source styling."""

    color: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$", description="Primary color in hex format")
    short_label: str = Field(..., min_length=1, max_length=3, description="Short label for icons (1-3 chars)")


class SourceBase(BaseModel):
    """Base schema for source data."""

    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=500)
    ui_config: Optional[Dict[str, Any]] = Field(None, description="UI config: {color, short_label}")
    is_enabled: bool = True
    fetch_limit: int = Field(30, ge=1, le=100)


class SourceCreate(SourceBase):
    """Schema for creating a source."""

    slug: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z][a-z0-9_]*$")


class SourceUpdate(BaseModel):
    """Schema for updating a source."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=500)
    ui_config: Optional[Dict[str, Any]] = Field(None, description="UI config: {color, short_label}")
    is_enabled: Optional[bool] = None
    fetch_limit: Optional[int] = Field(None, ge=1, le=100)


class SourceResponse(SourceBase):
    """Schema for source API responses."""

    id: int
    slug: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SourceToggleRequest(BaseModel):
    """Schema for enabling/disabling a source."""

    is_enabled: bool
