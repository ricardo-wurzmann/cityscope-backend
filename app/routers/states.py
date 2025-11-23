"""State endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.city import City

router = APIRouter(prefix="/states", tags=["states"])


@router.get("")
def get_states(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all unique states (UF) with their regions."""
    # Query distinct UFs with their regions
    # Use group_by to get one record per UF (with its region)
    states = (
        db.query(City.uf, City.region)
        .group_by(City.uf, City.region)
        .order_by(City.uf)
        .all()
    )
    
    # Since each UF should have the same region, we can deduplicate by UF
    seen_ufs = set()
    result = []
    for uf, region in states:
        if uf not in seen_ufs:
            result.append({"uf": uf, "region": region})
            seen_ufs.add(uf)
    
    return result


@router.get("/{uf}/cities")
def get_cities_by_state(
    uf: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all cities for a specific state (UF)."""
    # Validate UF (2 characters)
    if len(uf) != 2:
        raise HTTPException(status_code=400, detail="UF must be exactly 2 characters")
    
    # Query cities for the state, ordered alphabetically
    cities = (
        db.query(City)
        .filter(City.uf == uf.upper())
        .order_by(City.name)
        .all()
    )
    
    if not cities:
        raise HTTPException(status_code=404, detail=f"No cities found for state {uf.upper()}")
    
    return [
        {
            "id": city.id,
            "name": city.name,
            "uf": city.uf,
            "region": city.region,
        }
        for city in cities
    ]

