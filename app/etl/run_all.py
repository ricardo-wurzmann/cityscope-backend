"""Management command to run all ETL scripts."""

from app.etl.ibge.cities import load_cities
from app.etl.ibge.population import load_population
from app.etl.ibge.density import load_density


def main():
    """Run all ETL loaders in sequence."""
    print("=" * 60)
    print("CityScope ETL Pipeline - IBGE Data Loading")
    print("=" * 60)
    print()
    
    # Step 1: Load cities
    print("Step 1: Loading cities...")
    load_cities()
    print()
    
    # Step 2: Load population
    print("Step 2: Loading population data...")
    load_population()
    print()
    
    # Step 3: Compute density
    print("Step 3: Computing density values...")
    load_density()
    print()
    
    print("=" * 60)
    print("✓ ETL process completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
