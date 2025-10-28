# Country Currency & Exchange API

A RESTful API that fetches country data from external APIs, stores it in a database, and provides CRUD operations.

## Features

- Fetch and cache country data from external APIs
- Filter countries by region and currency
- Sort countries by estimated GDP
- Generate and serve summary images
- Full CRUD operations for country records
- Comprehensive error handling

## Requirements

- Python 3.11+
- PostgreSQL
- Dependencies listed in requirements.txt

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:

   - Create a PostgreSQL database
   - Update database configuration in `.env`
   - Tables will be created automatically on first run

6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### `POST /countries/refresh`

- Fetch all countries and exchange rates, then cache them in the database
- Returns total countries and last refresh timestamp

### `GET /countries`

- Get all countries from the DB
- Query parameters:
  - `region`: Filter by region (e.g., Africa)
  - `currency`: Filter by currency code (e.g., NGN)
  - `sort`: Sort by GDP (gdp_desc or gdp_asc)

### `GET /countries/{name}`

- Get one country by name
- Returns 404 if country not found

### `DELETE /countries/{name}`

- Delete a country record
- Returns 404 if country not found

### `GET /status`

- Show total countries and last refresh timestamp

### `GET /countries/image`

- Serve summary image showing statistics about countries
- Returns 404 if image not found

## Error Handling

The API returns consistent JSON error responses:

- 400 Bad Request: Validation errors
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server-side errors
- 503 Service Unavailable: External API issues

## Testing

Run tests with:

```bash
python -m pytest
```

## Environment Variables

- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `DB_NAME`: Database name
- `API_PORT`: API server port
- `API_HOST`: API server host
- `EXTERNAL_API_TIMEOUT`: External API timeout in seconds
