# Stock Prediction and Recommendation API

A FastAPI-based application that provides stock price predictions and trading recommendations using historical market data.

## Features

- Retrieve historical stock data
- Generate price predictions using machine learning
- Get trading recommendations based on technical analysis
- RESTful API with OpenAPI documentation
- Secure and scalable architecture
- Dependency management with Poetry

## Prerequisites

- Python 3.11+
- PostgreSQL database
- [Poetry](https://python-poetry.org/docs/#installation) (Python package and dependency manager)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/stock-predictions.git
   cd stock-predictions
   ```

2. Install Poetry (if not already installed):

   ```bash
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
   
   # macOS/Linux
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install project dependencies using Poetry:

   ```bash
   poetry install
   ```

   This will create a virtual environment and install all required dependencies.

4. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file with your database credentials and other settings.

5. Initialize the database:

   ```bash
   poetry run alembic upgrade head
   ```

## Running the Application

### Development Mode

Start the development server using FastAPI's auto-reload feature:

```bash
poetry run uvicorn src.main:app --reload
```

Or using the installed script:

```bash
# Install the package in development mode
poetry install

# Start the application
poetry run start
```

For development with auto-reload:

```bash
poetry run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### Production Deployment

For production deployment, it's recommended to use a production-grade ASGI server like Uvicorn with Gunicorn:

1. First, install the production dependencies:

   ```bash
   poetry install --no-dev
   ```

2. Run the application using Gunicorn with Uvicorn workers:

   ```bash
   poetry run gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

   This will start the application with 4 worker processes, which is a good starting point for production.

3. For better performance, you can adjust the number of workers based on your server's CPU cores:

   ```bash
   NUM_WORKERS=$((2 * $(nproc) + 1))
   poetry run gunicorn src.main:app --workers $NUM_WORKERS --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

4. For production, you should also set up:
   - A reverse proxy (Nginx, Apache, or similar)
   - Process manager (systemd, Supervisor, or similar)
   - Proper logging and monitoring
   - HTTPS using Let's Encrypt

## API Documentation

Once the application is running, you can access:

- Interactive API documentation: `http://localhost:8000/docs`
- Alternative documentation: `http://localhost:8000/redoc`

## Available Endpoints

### Stock Data
- `GET /api/stocks/{ticker}` - Get historical stock data
- `POST /api/stocks/{ticker}/predict` - Get price predictions
- `GET /api/stocks/{ticker}/recommendation` - Get trading recommendation

## Example Usage

### Get Historical Data

```bash
curl "http://localhost:8000/api/stocks/AAPL?start_date=2023-01-01&end_date=2023-12-31"
```

### Get Price Predictions

```bash
curl -X POST "http://localhost:8000/api/stocks/AAPL/predict" \
     -H "Content-Type: application/json" \
     -d '{"days": 7}'
```

### Get Trading Recommendation

```bash
curl "http://localhost:8000/api/stocks/AAPL/recommendation"
```

## Development

### Running Tests

Run the test suite with coverage:

```bash
poetry run pytest --cov=src --cov-report=term-missing
```

### Code Formatting

Format code with Black and sort imports with isort:

```bash
poetry run black .
poetry run isort .
```

### Linting

Run linters:

```bash
poetry run flake8
poetry run mypy src
```

## Project Structure

```
src/
├── api/               # API endpoints
├── config.py          # Application configuration
├── database.py        # Database connection
├── main.py            # FastAPI application
├── models/            # Database models
├── schemas/           # Pydantic models
└── services/          # Business logic
```

## License

MIT
