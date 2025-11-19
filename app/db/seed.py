from db.session import SessionLocal
from models.city import City
from models.indicator import Indicator
from models.indicator_value import IndicatorValue

def run():
    db = SessionLocal()

    # Exemplo de cidade
    sp = City(
        name="São Paulo",
        uf="SP",
    )
    db.add(sp)
    db.commit()
    db.refresh(sp)

    # Exemplo de indicador
    ind_pop = Indicator(
        code="POP",
        name="População",
        description="População total do município",
        unit="habitantes",
    )
    db.add(ind_pop)
    db.commit()
    db.refresh(ind_pop)

    # Valor do indicador para SP
    val = IndicatorValue(
        city_id=sp.id,
        indicator_id=ind_pop.id,
        year=2024,
        value=12345678,
    )
    db.add(val)
    db.commit()

    db.close()

if __name__ == "__main__":
    run()
