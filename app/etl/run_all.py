"""Management command to run all ETL scripts."""

from app.etl.ibge.download_cities import load_cities
from app.etl.ibge.download_indicators import load_population

if __name__ == "__main__":
    print("Loading cities...")
    load_cities()
    print("Loading population data...")
    load_population()
    print("ETL process completed!")

