"""City endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.deps import get_current_user
from db.session import get_db
from models.city import City
from models.indicator import Indicator
from models.indicator_value import IndicatorValue
from schemas.city import CityCreate, CityRead


router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("")
def list_cities(uf: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(City)
    if uf:
        q = q.filter(City.uf == uf.upper())
    return [{"id": c.id, "name": c.name, "uf": c.uf} for c in q.order_by(City.uf, City.name).limit(2000)]


@router.get("/{city_id}/indicators")
def city_indicators(city_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (
        db.query(IndicatorValue, Indicator)
        .join(Indicator, Indicator.id == IndicatorValue.indicator_id)
        .filter(IndicatorValue.city_id == city_id)
        .all()
    )
    return [
        {"indicator": ind.code, "name": ind.name, "unit": ind.unit, "year": iv.year, "value": iv.value}
        for iv, ind in rows
    ]

@router.post("", response_model=CityRead, status_code=status.HTTP_201_CREATED)
def create_city(city: CityCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Create a new city record."""
    # Verifica se já existe cidade com mesmo IBGE
    existing = db.query(City).filter(City.ibge_code == city.ibge_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="City already exists with this IBGE code")

    db_city = City(**city.model_dump())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

