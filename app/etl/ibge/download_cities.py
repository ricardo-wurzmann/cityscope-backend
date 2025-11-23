"""Download and load city list from IBGE."""

import requests
from app.db.session import SessionLocal
from app.models.city import City

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


def load_cities():
    """Load cities from IBGE API into the database."""
    db = SessionLocal()
    try:
        r = requests.get(IBGE_URL)
        r.raise_for_status()
        data = r.json()
        
        for item in data:
            city = City(
                ibge_id=item["id"],
                name=item["nome"],
                uf=item["microrregiao"]["mesorregiao"]["UF"]["sigla"],
                region=item["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
            )
            db.add(city)
        
        db.commit()
        print(f"Loaded {len(data)} cities from IBGE")
    except Exception as e:
        db.rollback()
        print(f"Error loading cities: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_cities()

