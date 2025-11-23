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
    indicator_code: str
    indicator_name: str
    year: int | None
    value: float
    unit: str | None

    class Config:
        from_attributes = True


