"""Simple ETL helpers to seed the database with sample data."""

from __future__ import annotations

from sqlalchemy.orm import Session

from core.security import hash_password
from models.city import City
from models.indicator import Indicator
from models.indicator_value import IndicatorValue
from models.user import User


def ensure_superuser(db: Session, email: str, password: str) -> User:
    """Create a superuser if it does not exist."""

    user = db.query(User).filter(User.email == email).one_or_none()
    if user is None:
        user = User(
            email=email,
            full_name="Administrator",
            hashed_password=hash_password(password),
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def seed_sample_data(db: Session) -> None:
    """Insert a minimal dataset useful for local development."""

    ensure_superuser(db, "admin@cityscope.local", "change-me")

    city = db.query(City).filter(City.ibge_code == "3550308").one_or_none()
    if city is None:
        city = City(name="São Paulo", state="SP", region="Sudeste", ibge_code="3550308")
        db.add(city)
        db.commit()
        db.refresh(city)

    indicator = db.query(Indicator).filter(Indicator.slug == "population").one_or_none()
    if indicator is None:
        indicator = Indicator(
            name="Population",
            slug="population",
            description="Total estimated population",
            unit="people",
            source="IBGE",
        )
        db.add(indicator)
        db.commit()
        db.refresh(indicator)

    exists = (
        db.query(IndicatorValue)
        .filter(
            IndicatorValue.indicator_id == indicator.id,
            IndicatorValue.city_id == city.id,
            IndicatorValue.reference_year == 2023,
        )
        .one_or_none()
    )
    if exists is None:
        value = IndicatorValue(
            indicator_id=indicator.id,
            city_id=city.id,
            reference_year=2023,
            value=11253503,
        )
        db.add(value)
        db.commit()


