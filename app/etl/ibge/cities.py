"""Load city metadata from IBGE API."""

import requests
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.city import City
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


def load_cities():
    """Load cities from IBGE API with upsert logic."""
    db = SessionLocal()
    try:
        # Ensure AREA indicator exists
        area_indicator = db.query(Indicator).filter(Indicator.code == "AREA").first()
        if not area_indicator:
            area_indicator = Indicator(
                code="AREA",
                name="Territorial Area",
                unit="km²"
            )
            db.add(area_indicator)
            db.commit()
            db.refresh(area_indicator)
            print("✓ Created AREA indicator")
        else:
            print("✓ AREA indicator already exists")
        
        print("Fetching cities from IBGE API...")
        r = requests.get(IBGE_URL)
        r.raise_for_status()
        data = r.json()
        
        print(f"Processing {len(data)} cities...")
        loaded = 0
        updated = 0
        area_values_created = 0
        
        for item in data:
            ibge_id = item["id"]
            name = item["nome"]
            uf = item["microrregiao"]["mesorregiao"]["UF"]["sigla"]
            region = item["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
            
            # Try to get area from the item (may not be present)
            area = item.get("area")
            if area is not None:
                try:
                    area = float(area)
                except (ValueError, TypeError):
                    area = None
            
            # Upsert logic
            city = db.query(City).filter(City.ibge_id == ibge_id).first()
            if city:
                # Update existing city
                city.name = name
                city.uf = uf
                city.region = region
                if area is not None:
                    city.area = area
                updated += 1
            else:
                # Create new city
                city = City(
                    ibge_id=ibge_id,
                    name=name,
                    uf=uf,
                    region=region,
                    area=area
                )
                db.add(city)
                loaded += 1
            
            # Commit to get city.id
            db.flush()
            
            # Create/update AREA indicator value if area is available
            if area is not None and area > 0:
                area_value = db.query(IndicatorValue).filter(
                    IndicatorValue.city_id == city.id,
                    IndicatorValue.indicator_id == area_indicator.id,
                    IndicatorValue.year.is_(None)
                ).first()
                
                if area_value:
                    area_value.value = area
                else:
                    area_value = IndicatorValue(
                        city_id=city.id,
                        indicator_id=area_indicator.id,
                        year=None,
                        value=area
                    )
                    db.add(area_value)
                    area_values_created += 1
        
        db.commit()
        print(f"✓ Loaded {loaded} new cities, updated {updated} existing cities")
        print(f"✓ Created/updated {area_values_created} AREA indicator values")
        return loaded + updated
    except Exception as e:
        db.rollback()
        print(f"✗ Error loading cities: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_cities()

