"""City endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.city import City
from app.schemas.city import CityCreate, CityRead


router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("")
def get_cities(
    page: int = 1,
    limit: int = 50,
    uf: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get cities with pagination."""
    skip = (page - 1) * limit
    q = db.query(City)
    if uf:
        q = q.filter(City.uf == uf.upper())
    cities = q.order_by(City.uf, City.name).offset(skip).limit(limit).all()
    return [{"id": c.id, "name": c.name, "uf": c.uf, "region": c.region} for c in cities]


@router.get("/debug/token")
def debug_token(user=Depends(get_current_user)):
    return {"message": "OK", "user": user.email}


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

