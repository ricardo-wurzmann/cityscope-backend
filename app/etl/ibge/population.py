"""Load population data from IBGE SIDRA table 6579."""

import requests
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.city import City
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue

SIDRA_URL = "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/93/p/all"


def load_population():
    """Load population estimate data from IBGE SIDRA table 6579."""
    db = SessionLocal()
    try:
        # Ensure POP indicator exists
        pop_indicator = db.query(Indicator).filter(Indicator.code == "POP").first()
        if not pop_indicator:
            pop_indicator = Indicator(
                code="POP",
                name="Population",
                unit="people"
            )
            db.add(pop_indicator)
            db.commit()
            db.refresh(pop_indicator)
            print("✓ Created POP indicator")
        else:
            print("✓ POP indicator already exists")
        
        print("Fetching population data from IBGE SIDRA...")
        r = requests.get(SIDRA_URL)
        r.raise_for_status()
        data = r.json()
        
        # Skip header row (first row)
        rows = data[1:] if len(data) > 1 else []
        
        print(f"Processing {len(rows)} population records...")
        loaded = 0
        updated = 0
        
        # Create a mapping of ibge_id to city_id for faster lookups
        cities_map = {city.ibge_id: city.id for city in db.query(City).all()}
        
        for row in rows:
            try:
                # Extract data from SIDRA response
                # Format: D1C = city code (IBGE), D3C = year, V = value
                ibge_id_str = row.get("D1C", "")
                year_str = row.get("D3C", "")
                value_str = row.get("V", "")
                
                if not ibge_id_str or not year_str or not value_str:
                    continue
                
                ibge_id = int(ibge_id_str)
                year = int(year_str)
                value = float(value_str)
                
                # Find city by ibge_id
                city_id = cities_map.get(ibge_id)
                if not city_id:
                    continue  # Skip if city not found
                
                # Check if value already exists
                existing = db.query(IndicatorValue).filter(
                    IndicatorValue.city_id == city_id,
                    IndicatorValue.indicator_id == pop_indicator.id,
                    IndicatorValue.year == year
                ).first()
                
                if existing:
                    # Update existing value
                    existing.value = value
                    updated += 1
                else:
                    # Create new value
                    indicator_value = IndicatorValue(
                        city_id=city_id,
                        indicator_id=pop_indicator.id,
                        year=year,
                        value=value
                    )
                    db.add(indicator_value)
                    loaded += 1
                
            except (ValueError, KeyError) as e:
                print(f"  Warning: Error processing row: {e}")
                continue
        
        db.commit()
        print(f"✓ Loaded {loaded} new population values, updated {updated} existing values")
        return loaded + updated
    except Exception as e:
        db.rollback()
        print(f"✗ Error loading population data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_population()

