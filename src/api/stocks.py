from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from ..database import get_db
from ..schemas.stock import Stock, StockPredictionRequest, StockPrediction, StockRecommendation
from ..services.stock_service import StockService

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{ticker}", response_model=List[Stock])
async def get_stock_data(
    ticker: str,
    start_date: date = date.today() - timedelta(days=30),
    end_date: date = date.today(),
    db: Session = Depends(get_db)
):
    """
    Retrieve historical stock data for a given ticker and date range.
    
    - **ticker**: Stock ticker symbol (e.g., 'AAPL')
    - **start_date**: Start date in YYYY-MM-DD format (default: 30 days ago)
    - **end_date**: End date in YYYY-MM-DD format (default: today)
    """
    stock_service = StockService(db)
    stocks = stock_service.get_stock_data(ticker.upper(), start_date, end_date)
    if not stocks:
        raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker} in the specified date range")
    return stocks

@router.post("/{ticker}/predict", response_model=List[StockPrediction])
async def predict_stock_price(
    ticker: str,
    prediction_request: StockPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict stock prices for the next N days.
    
    - **ticker**: Stock ticker symbol (e.g., 'AAPL')
    - **days**: Number of days to predict (1-30)
    """
    stock_service = StockService(db)
    predictions = stock_service.predict_stock_price(
        ticker.upper(), 
        days=min(prediction_request.days, 30)  # Cap at 30 days
    )
    
    if not predictions:
        raise HTTPException(
            status_code=404, 
            detail=f"Insufficient data to generate predictions for {ticker}"
        )
    return predictions

@router.get("/{ticker}/recommendation", response_model=StockRecommendation)
async def get_stock_recommendation(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    Get a trading recommendation for a stock based on technical analysis.
    
    - **ticker**: Stock ticker symbol (e.g., 'AAPL')
    """
    stock_service = StockService(db)
    recommendation = stock_service.get_stock_recommendation(ticker.upper())
    
    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail=f"Could not generate recommendation for {ticker}. Insufficient data."
        )
    return recommendation
