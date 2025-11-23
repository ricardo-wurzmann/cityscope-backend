from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    ibge_id = Column(Integer, unique=True, index=True)   # IBGE official ID
    name = Column(String, index=True)
    uf = Column(String(2), index=True)
    region = Column(String, index=True, nullable=True)

    indicators = relationship("IndicatorValue", back_populates="city")
