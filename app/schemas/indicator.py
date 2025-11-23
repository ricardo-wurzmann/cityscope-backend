"""Indicator and indicator value schemas."""

from pydantic import BaseModel


class IndicatorBase(BaseModel):
    code: str
    name: str
    unit: str | None = None


class IndicatorValueBase(BaseModel):
    city_id: int
    indicator_id: int
    year: int
    value: float


class IndicatorValueOut(BaseModel):
    indicator: str
    value: float
    unit: str | None
    year: int

    class Config:
        from_attributes = True


