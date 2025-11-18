"""City schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class CityBase(BaseModel):
    name: str = Field(..., max_length=255)
    state: str = Field(..., min_length=2, max_length=2, description="Brazilian state acronym")
    region: str | None = Field(default=None, max_length=32)
    ibge_code: str = Field(..., max_length=20)
    latitude: float | None = None
    longitude: float | None = None


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    region: str | None = Field(default=None, max_length=32)
    latitude: float | None = None
    longitude: float | None = None


class CityRead(CityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


