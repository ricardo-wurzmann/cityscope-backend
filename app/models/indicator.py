from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True)       # IBGE table code (SIDRA)
    name = Column(String, index=True)
    unit = Column(String, nullable=True)

    values = relationship("IndicatorValue", back_populates="indicator")
