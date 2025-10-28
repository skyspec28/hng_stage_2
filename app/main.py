from typing import List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from . import models, utils, schemas
from .database import get_db, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Country Currency & Exchange API",
    description="API for retrieving and managing country currencies and exchange rates",
    version="1.0.0",
    include_in_schema=True
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_details = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if str(loc) != "body")
        field = field_path or "body"
        error_details[field] = error["msg"]
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation failed",
            "details": error_details
        }
    )

@app.exception_handler(utils.ExternalAPIError)
async def external_api_exception_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={
            "error": "External data source unavailable",
            "details": str(exc)
        }
    )

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database error",
            "message": "An error occurred while accessing the database"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

@app.get("/countries/refresh")
async def get_refresh_not_allowed():
    raise HTTPException(
        status_code=405,
        detail="Method not allowed. Use POST to refresh countries data."
    )

@app.post("/countries/refresh", response_model=schemas.StatusResponse)
async def refresh_countries(request: Optional[schemas.RefreshRequest] = None, db: Session = Depends(get_db)):
    countries_data = utils.fetch_country_data()
    exchange_rates = utils.fetch_exchange_rates()
    
    refresh_time = datetime.utcnow()
    
    for country_data in countries_data:
        country_dict = utils.extract_country_data(country_data, exchange_rates)
        db_country = db.query(models.Country).filter(
            models.Country.name.ilike(country_dict["name"])
        ).first()
        
        if db_country:
            for key, value in country_dict.items():
                setattr(db_country, key, value)
        else:
            db_country = models.Country(**country_dict)
            db.add(db_country)
    
    db.commit()
    total_countries = db.query(models.Country).count()
    
    return {"total_countries": total_countries, "last_refreshed_at": refresh_time}

@app.get("/countries", response_model=List[schemas.CountryResponse])
async def get_countries(
    region: Optional[str] = None,
    currency: Optional[str] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Country)
    if region:
        query = query.filter(models.Country.region == region)
    if currency:
        query = query.filter(models.Country.currency_code == currency.upper())
    if sort == "gdp_desc":
        query = query.order_by(models.Country.estimated_gdp.desc())
    elif sort == "gdp_asc":
        query = query.order_by(models.Country.estimated_gdp.asc())
    
    return query.all()

@app.get("/countries/image")
async def get_summary_image(db: Session = Depends(get_db)):
    image_path = Path("cache/summary.png")
    if image_path.is_file():
        return FileResponse(
            str(image_path),
            media_type="image/png",
            filename="summary.png"
        )

    total_countries = db.query(models.Country).count()
    if total_countries == 0:
        raise HTTPException(
            status_code=404,
            detail="Summary image not found"
        )
    top_gdp_countries = db.query(models.Country)\
        .filter(models.Country.estimated_gdp.isnot(None))\
        .order_by(models.Country.estimated_gdp.desc())\
        .limit(5)\
        .all()
    
    if not top_gdp_countries:
        raise HTTPException(
            status_code=404,
            detail="Summary image not found"
        )

    last_refresh = db.query(models.Country.last_refreshed_at)\
        .order_by(models.Country.last_refreshed_at.desc())\
        .first()

    try:
        utils.generate_summary_image(
            total_countries,
            [
                {
                    "name": country.name,
                    "estimated_gdp": country.estimated_gdp
                }
                for country in top_gdp_countries
            ],
            last_refresh[0] if last_refresh else datetime.utcnow()
        )

        return FileResponse(
            str(image_path),
            media_type="image/png",
            filename="summary.png"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate or serve summary image"
        )

@app.get("/countries/{name}", response_model=schemas.CountryResponse)
async def get_country(name: str, db: Session = Depends(get_db)):
    country = db.query(models.Country).filter(models.Country.name == name).first()
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )
    return country

@app.delete("/countries/{name}")
async def delete_country(name: str, db: Session = Depends(get_db)):
    country = db.query(models.Country).filter(models.Country.name == name).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    db.delete(country)
    db.commit()
    return {"status": "success", "message": f"Country {name} deleted successfully"}

@app.get("/status", response_model=schemas.StatusResponse)
async def get_status(db: Session = Depends(get_db)):
    try:
        total_countries = db.query(models.Country).count()
        last_refresh = db.query(models.Country.last_refreshed_at)\
            .order_by(models.Country.last_refreshed_at.desc())\
            .first()

        return schemas.StatusResponse(
            total_countries=total_countries,
            last_refreshed_at=last_refresh[0] if last_refresh else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) from e

