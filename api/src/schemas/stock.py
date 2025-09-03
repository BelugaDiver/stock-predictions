from datetime import date, time
from pydantic import BaseModel, Field
from typing import Optional, List

class StockBase(BaseModel):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: str
    time: time
    
    class Config:
        from_attributes = True

class StockPredictionRequest(BaseModel):
    days: int = Field(gt=0, le=30, description="Number of days to predict")

class StockPrediction(BaseModel):
    date: date
    predicted_close: float
    confidence_interval_lower: float
    confidence_interval_upper: float

class StockRecommendation(BaseModel):
    ticker: str
    current_price: float
    target_price: float
    recommendation: str  # 'STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'
    confidence: float  # 0.0 to 1.0
    last_updated: date
