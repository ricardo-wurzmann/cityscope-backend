"""Download and load indicator data from IBGE SIDRA API."""

import requests
from app.db.session import SessionLocal
from app.models.city import City
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue


def load_population():
    """Load population estimate data from IBGE SIDRA table 6579."""
    db = SessionLocal()
    try:
        # Create Indicator if not exists
        pop = db.query(Indicator).filter(Indicator.code == "6579").first()
        if not pop:
            pop = Indicator(code="6579", name="Population Estimate", unit="people")
            db.add(pop)
            db.commit()
            db.refresh(pop)
        else:
            db.refresh(pop)
        
        cities = db.query(City).all()
        total_loaded = 0
        
        for city in cities:
            url = f"https://apisidra.ibge.gov.br/values/t/6579/n6/{city.ibge_id}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Skip header row (first row)
                for row in data[1:]:
                    try:
                        year = int(row["D3C"])
                        value = float(row["V"])
                        
                        indicator_value = IndicatorValue(
                            city_id=city.id,
                            indicator_id=pop.id,
                            year=year,
                            value=value
                        )
                        db.add(indicator_value)
                        total_loaded += 1
                    except (ValueError, KeyError) as e:
                        print(f"Error processing row for city {city.id}: {e}")
                        continue
                
            except requests.RequestException as e:
                print(f"Error fetching data for city {city.id} (IBGE {city.ibge_id}): {e}")
                continue
        
        db.commit()
        print(f"Loaded {total_loaded} population indicator values")
    except Exception as e:
        db.rollback()
        print(f"Error loading population data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_population()

