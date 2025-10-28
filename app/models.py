from sqlalchemy import Column, Integer, String, Float, DateTime, func
from .database import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    capital = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True, index=True)
    population = Column(Integer, nullable=False)
    currency_code = Column(String(3), nullable=True)
    exchange_rate = Column(Float, nullable=True)
    estimated_gdp = Column(Float, nullable=True)
    flag_url = Column(String(255), nullable=True)
    last_refreshed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
