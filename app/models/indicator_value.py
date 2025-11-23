from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class IndicatorValue(Base):
    __tablename__ = "indicator_values"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    indicator_id = Column(Integer, ForeignKey("indicators.id"))
    year = Column(Integer, nullable=True)  # Nullable for static indicators like AREA
    value = Column(Float)

    city = relationship("City", back_populates="indicators")
    indicator = relationship("Indicator", back_populates="values")

