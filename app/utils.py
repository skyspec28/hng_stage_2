import os
import requests
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from requests.exceptions import RequestException
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class ExternalAPIError(Exception):
    pass

def fetch_country_data() -> List[Dict[str, Any]]:
    url = 'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # API returns list of country objects directly
        if isinstance(data, list):
            return data
        return data.get('data', [])
    except Exception as e:
        raise ExternalAPIError(f"Could not fetch data from Countries API: {str(e)}")

def fetch_exchange_rates() -> Dict[str, float]:
    url = 'https://open.er-api.com/v6/latest/USD'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('rates', {})
    except Exception as e:
        raise ExternalAPIError(f"Could not fetch data from Exchange Rates API: {str(e)}")

def compute_estimated_gdp(population: int, exchange_rate: Optional[float]) -> Optional[float]:
    if not exchange_rate:
        return None
    
    # Fresh random multiplier for each calculation
    gdp_per_capita = random.uniform(1000, 2000)
    return (population * gdp_per_capita) / exchange_rate

def extract_country_data(country_data: Dict[str, Any], exchange_rates: Dict[str, float]) -> Dict[str, Any]:
    """
    Extract and transform country data for database storage.
    Handles missing or invalid data according to requirements.
    """
    # Extract first currency code if available
    currencies = country_data.get('currencies', [])
    currency_code = currencies[0].get('code') if currencies else None
    
    # Get exchange rate if currency code is available
    exchange_rate = exchange_rates.get(currency_code) if currency_code else None
    
    # Calculate estimated GDP and ensure population is valid
    population = country_data.get('population', 0)
    if population <= 0:
        population = 1000000  # Use a default population if missing or invalid
    
    estimated_gdp = compute_estimated_gdp(population, exchange_rate) if exchange_rate else None
    
    return {
        'name': country_data.get('name'),
        'capital': country_data.get('capital'),
        'region': country_data.get('region'),
        'population': population,
        'currency_code': currency_code,
        'exchange_rate': exchange_rate,
        'estimated_gdp': estimated_gdp,
        'flag_url': country_data.get('flag'),
        'last_refreshed_at': datetime.utcnow()
    }

def generate_summary_image(total_countries: int, top_gdp_countries: List[Dict[str, Any]], last_refresh: datetime) -> str:
    """
    Generate a summary image with country statistics
    Returns the path to the generated image
    """
    # Create cache directory if it doesn't exist
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)
    image_path = cache_dir / "summary.png"

    # Create a new image with a white background
    width = 800
    height = 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    # Draw title
    draw.text((50, 50), "Country API Summary", fill='black', font=font)
    
    # Draw statistics
    y_pos = 100
    draw.text((50, y_pos), f"Total Countries: {total_countries}", fill='black', font=font)
    draw.text((50, y_pos + 40), f"Last Refresh: {last_refresh.strftime('%Y-%m-%d %H:%M:%S UTC')}", fill='black', font=font)
    
    # Draw top 5 countries by GDP
    y_pos += 100
    draw.text((50, y_pos), "Top 5 Countries by Estimated GDP:", fill='black', font=font)
    y_pos += 40
    
    for country in top_gdp_countries[:5]:
        gdp_text = f"{country['name']}: ${country['estimated_gdp']:,.2f}"
        draw.text((70, y_pos), gdp_text, fill='black', font=font)
        y_pos += 30

    # Save the image
    image.save(str(image_path))
    return str(image_path)