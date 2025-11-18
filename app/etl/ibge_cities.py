"""Utilities to load Brazilian city metadata from IBGE datasets."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session

from models.city import City


@dataclass(frozen=True)
class IBGECityRecord:
    """Represents a row from the IBGE city dataset."""

    name: str
    state: str
    region: str
    ibge_code: str
    latitude: float | None
    longitude: float | None

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "IBGECityRecord":
        def parse_float(value: str) -> float | None:
            return float(value) if value else None

        return cls(
            name=data["name"],
            state=data["state"],
            region=data.get("region", ""),
            ibge_code=data["ibge_code"],
            latitude=parse_float(data.get("latitude", "")),
            longitude=parse_float(data.get("longitude", "")),
        )


def read_ibge_csv(path: Path) -> Iterable[IBGECityRecord]:
    """Yield `IBGECityRecord` instances from a CSV file."""

    with path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield IBGECityRecord.from_dict(row)


def load_ibge_cities(db: Session, records: Iterable[IBGECityRecord]) -> int:
    """Persist the provided records to the database.

    Returns the number of inserted or updated cities.
    """

    count = 0
    for record in records:
        city = db.query(City).filter(City.ibge_code == record.ibge_code).one_or_none()
        if city is None:
            city = City(
                name=record.name,
                state=record.state,
                region=record.region or None,
                ibge_code=record.ibge_code,
                latitude=record.latitude,
                longitude=record.longitude,
            )
            db.add(city)
            count += 1
        else:
            city.name = record.name
            city.state = record.state
            city.region = record.region or None
            city.latitude = record.latitude
            city.longitude = record.longitude
    db.commit()
    return count


