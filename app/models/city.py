from sqlalchemy import Column, Integer, String

from db.base import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)       # id IBGE, se quiser
    name = Column(String(255), index=True)
    uf = Column(String(2), index=True)
