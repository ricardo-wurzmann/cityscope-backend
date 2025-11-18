"""Indicator and indicator value schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class IndicatorBase(BaseModel):
    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    description: str | None = None
    unit: str | None = Field(default=None, max_length=64)
    source: str | None = Field(default=None, max_length=255)


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    unit: str | None = Field(default=None, max_length=64)
    source: str | None = Field(default=None, max_length=255)


class IndicatorRead(IndicatorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IndicatorValueBase(BaseModel):
    indicator_id: int
    city_id: int
    reference_year: int
    value: float


class IndicatorValueCreate(IndicatorValueBase):
    pass


class IndicatorValueRead(IndicatorValueBase):
    id: int
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


