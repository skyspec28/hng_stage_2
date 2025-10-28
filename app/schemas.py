from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CountryBase(BaseModel):
    name: str = Field(..., description="Country name (required)")
    capital: Optional[str] = Field(None, description="Capital city name (optional)")
    region: Optional[str] = Field(None, description="Geographic region (optional)")
    population: int = Field(..., description="Total population (required)", gt=0)
    currency_code: Optional[str] = Field(None, description="3-letter currency code", min_length=3, max_length=3)
    flag_url: Optional[str] = Field(None, description="URL to country flag image (optional)")

class CountryCreate(CountryBase):
    pass

class CountryResponse(CountryBase):
    id: int
    exchange_rate: Optional[float] = Field(None, description="Currency exchange rate to USD")
    estimated_gdp: Optional[float] = Field(None, description="Estimated GDP based on population and exchange rate")
    last_refreshed_at: datetime = Field(..., description="Last data refresh timestamp")

    class Config:
        from_attributes = True

class StatusResponse(BaseModel):
    total_countries: int = Field(..., description="Total number of countries in database")
    last_refreshed_at: Optional[datetime] = Field(None, description="Timestamp of last data refresh")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

class RefreshRequest(BaseModel):
    """Schema for refresh request with validation."""
    force: bool = Field(default=True, description="Force refresh even if data was recently updated")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "force": True
            }
        }