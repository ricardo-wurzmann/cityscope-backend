"""Compute and load population density (POP / AREA)."""

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.city import City
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue


def load_density():
    """Compute density = population / area for all cities and years."""
    db = SessionLocal()
    try:
        # Ensure DENSITY indicator exists
        density_indicator = db.query(Indicator).filter(Indicator.code == "DENSITY").first()
        if not density_indicator:
            density_indicator = Indicator(
                code="DENSITY",
                name="Population Density",
                unit="people/km²"
            )
            db.add(density_indicator)
            db.commit()
            db.refresh(density_indicator)
            print("✓ Created DENSITY indicator")
        else:
            print("✓ DENSITY indicator already exists")
        
        # Ensure AREA indicator exists (for consistency)
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
        
        # Get POP indicator
        pop_indicator = db.query(Indicator).filter(Indicator.code == "POP").first()
        if not pop_indicator:
            print("✗ POP indicator not found. Please run population loader first.")
            return 0
        
        print("Computing density values...")
        loaded = 0
        updated = 0
        
        # Get all cities with area
        cities = db.query(City).filter(City.area.isnot(None), City.area > 0).all()
        
        for city in cities:
            # Get all population values for this city
            pop_values = db.query(IndicatorValue).filter(
                IndicatorValue.city_id == city.id,
                IndicatorValue.indicator_id == pop_indicator.id
            ).all()
            
            # Also ensure AREA value exists for this city
            area_value = db.query(IndicatorValue).filter(
                IndicatorValue.city_id == city.id,
                IndicatorValue.indicator_id == area_indicator.id,
                IndicatorValue.year.is_(None)
            ).first()
            
            if not area_value:
                area_value = IndicatorValue(
                    city_id=city.id,
                    indicator_id=area_indicator.id,
                    year=None,
                    value=city.area
                )
                db.add(area_value)
                db.commit()
            
            # Compute density for each year with population data
            for pop_value in pop_values:
                if pop_value.value and city.area:
                    density = pop_value.value / city.area
                    
                    # Check if density value already exists
                    existing = db.query(IndicatorValue).filter(
                        IndicatorValue.city_id == city.id,
                        IndicatorValue.indicator_id == density_indicator.id,
                        IndicatorValue.year == pop_value.year
                    ).first()
                    
                    if existing:
                        existing.value = density
                        updated += 1
                    else:
                        density_value = IndicatorValue(
                            city_id=city.id,
                            indicator_id=density_indicator.id,
                            year=pop_value.year,
                            value=density
                        )
                        db.add(density_value)
                        loaded += 1
        
        db.commit()
        print(f"✓ Loaded {loaded} new density values, updated {updated} existing values")
        return loaded + updated
    except Exception as e:
        db.rollback()
        print(f"✗ Error computing density: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_density()

