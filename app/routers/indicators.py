"""Indicator endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.schemas.indicator import IndicatorValueOut

router = APIRouter(tags=["indicators"])


@router.get("/cities/{city_id}/indicators", response_model=list[IndicatorValueOut])
def get_indicators_by_city(city_id: int, db: Session = Depends(get_db)):
    """Get all indicator values for a given city."""
    values = (
        db.query(IndicatorValue)
        .join(Indicator)
        .filter(IndicatorValue.city_id == city_id)
        .all()
    )
    return [
        IndicatorValueOut(
            indicator_code=v.indicator.code,
            indicator_name=v.indicator.name,
            year=v.year,
            value=v.value,
            unit=v.indicator.unit
        )
        for v in values
    ]

