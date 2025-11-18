from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base import Base


class IndicatorValue(Base):
    __tablename__ = "indicator_values"

    id = Column(Integer, primary_key=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    year = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)

    indicator = relationship("Indicator")
    city = relationship("City")

    __table_args__ = (UniqueConstraint("indicator_id", "city_id", "year", name="uq_indicator_city_year"),)

