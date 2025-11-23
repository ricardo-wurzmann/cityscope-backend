import requests
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.city import City

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


def run():
    print("📥 Baixando lista de municípios do IBGE...")

    r = requests.get(IBGE_URL)
    r.raise_for_status()
    data = r.json()

    db: Session = SessionLocal()

    count = 0
    skipped = 0

    for item in data:
        try:
            name = item["nome"]
            ibge_id = item["id"]

            # --- TRATAMENTO SEGURO DE UF E REGIÃO ---
            microrregiao = item.get("microrregiao") or {}
            mesorregiao = microrregiao.get("mesorregiao") or {}
            uf_obj = mesorregiao.get("UF") or {}

            uf = uf_obj.get("sigla")
            region = uf_obj.get("regiao", {}).get("nome")

            if not uf:
                skipped += 1
                print(f"⚠️ Ignorando município sem UF: {name} ({ibge_id})")
                continue

            city = City(
                name=name,
                uf=uf,
                region=region,
                ibge_id=ibge_id,
            )
            db.add(city)
            count += 1

        except Exception as e:
            print(f"❌ Erro ao processar cidade {item}: {e}")
            skipped += 1

    db.commit()
    db.close()

    print(f"✅ Inseridas {count} cidades.")
    print(f"⚠️ Ignoradas {skipped} cidades sem info completa.")


if __name__ == "__main__":
    run()
