# Stock Prediction and Recommendation API

A FastAPI-based application that provides stock price predictions and trading recommendations using historical market data.

## Features

- Retrieve historical stock data
- Generate price predictions using machine learning
- Get trading recommendations based on technical analysis
- RESTful API with OpenAPI documentation
- Secure and scalable architecture

## Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stock-predictions.git
   cd stock-predictions
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your database credentials and other settings.

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

## Running the Application

Start the development server:
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

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
