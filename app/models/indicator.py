from sqlalchemy import Column, Integer, String, Text

from db.base import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    code = Column(String(64), unique=True, index=True)  # ex: POP
    name = Column(String(255))
    description = Column(Text)
    unit = Column(String(64))  # ex: habitantes
