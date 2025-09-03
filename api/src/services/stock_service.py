from typing import List, Optional, Tuple, Union
from datetime import date, timedelta
from functools import partial
import asyncio
import time
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from ..models.daily import Daily
from ..schemas.stock import Stock, StockPredictionRequest, StockPrediction, StockRecommendation
from ..telemetry_decorators import (
    trace_method, 
    measure_yfinance_call, 
    record_prediction_metrics,
    time_operation,
    log_method_call
)
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

# Model cache configuration
MODEL_CACHE_TTL = 300  # 5 minutes
CONFIDENCE_INTERVAL_RANGE = 0.02  # 2%

# Simple in-memory model cache
_model_cache = {}

class ModelCacheEntry:
    def __init__(self, model, scaler, features, created_at: float):
        self.model = model
        self.scaler = scaler
        self.features = features
        self.created_at = created_at
    
    def is_expired(self, ttl_seconds: int = MODEL_CACHE_TTL) -> bool:
        return time.time() - self.created_at > ttl_seconds

class StockService:
    def __init__(self):
        pass
    
    @trace_method("get_stock_data")
    @measure_yfinance_call("ticker")
    @log_method_call(include_args=True)
    async def get_stock_data(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        """Retrieve stock data for a given ticker and date range using Yahoo Finance, returns a DataFrame"""
        try:
            # Run yfinance in executor to avoid blocking event loop
            loop = asyncio.get_running_loop()
            df = await loop.run_in_executor(
                None, 
                partial(yf.download, ticker, start=start_date, end=end_date + timedelta(days=1), progress=False)
            )
            
            if df.empty:
                logger.warning(f"No data returned for ticker {ticker}")
                return pd.DataFrame()
            
            df = df.reset_index()
            df['Ticker'] = ticker
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()
    
    @trace_method("predict_stock_price")
    @record_prediction_metrics("ticker", "days", "random_forest")
    @log_method_call(include_args=True, include_result=True)
    async def predict_stock_price(
        self, 
        ticker: str, 
        days: int = 7,
        lookback_days: int = 90
    ) -> List[StockPrediction]:
        """
        Predict stock prices for the next 'days' days with model caching
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to predict
            lookback_days: Number of historical days to use for prediction
            
        Returns:
            List of StockPrediction objects with date and predicted close price
        """
        try:
            # Get historical data
            end_date = date.today()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Create cache key for model
            cache_key = f"{ticker}_{lookback_days}_{end_date}"
            
            # Check if model is cached and valid
            model, scaler, features = self._get_cached_model(cache_key, ticker, start_date, end_date)
            
            if model is None:
                return []
            
            # Get latest data for prediction base
            stocks = await self._fetch_historical_data(ticker, start_date, end_date)
            if stocks.empty:
                return []
            
            df = self._prepare_ml_data(stocks)
            if df is None:
                return []
            
            predictions = self._generate_predictions(model, scaler, df, features, end_date, days)
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting stock price for {ticker}: {e}")
            return []
    
    def _get_cached_model(self, cache_key: str, ticker: str, start_date: date, end_date: date) -> Tuple[Optional[RandomForestRegressor], Optional[MinMaxScaler], Optional[List[str]]]:
        """Get model from cache or train new one if expired/missing"""
        global _model_cache
        
        # Check if cached model exists and is valid
        if cache_key in _model_cache:
            entry = _model_cache[cache_key]
            if not entry.is_expired():
                logger.info(f"Using cached model for {ticker}")
                return entry.model, entry.scaler, entry.features
            else:
                logger.info(f"Model cache expired for {ticker}, retraining...")
                del _model_cache[cache_key]
        
        # Train new model and cache it
        logger.info(f"Training new model for {ticker}")
        
        # We need to fetch data synchronously here for training
        # This is acceptable as training happens infrequently due to caching
        try:
            df = yf.download(ticker, start=start_date, end=end_date + timedelta(days=1), progress=False)
            if df.empty:
                return None, None, None
                
            df = df.reset_index()
            df['Ticker'] = ticker
            df = self._prepare_ml_data(df)
            
            if df is None:
                return None, None, None
                
            model, scaler, features = self._train_model(df)
            
            if model is not None:
                # Cache the trained model
                _model_cache[cache_key] = ModelCacheEntry(model, scaler, features, time.time())
                logger.info(f"Model cached for {ticker}")
            
            return model, scaler, features
            
        except Exception as e:
            logger.error(f"Error training model for {ticker}: {e}")
            return None, None, None
    
    @trace_method("fetch_historical_data")
    async def _fetch_historical_data(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        """Fetch historical data for ML training"""
        return await self.get_stock_data(ticker, start_date, end_date)
    
    @trace_method("prepare_ml_data")
    def _prepare_ml_data(self, stocks: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Prepare data for ML model with feature engineering"""
        try:
            df = stocks.copy()
            df = df.sort_values('Date')
            
            # Feature engineering
            df['returns'] = df['Close'].pct_change()
            df['sma_5'] = df['Close'].rolling(window=5).mean()
            df['sma_20'] = df['Close'].rolling(window=20).mean()
            df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
            df = df.dropna()
            
            if len(df) < 30:  # Not enough data
                logger.warning("Insufficient data for ML training")
                return None
                
            return df
            
        except Exception as e:
            logger.error(f"Error preparing ML data: {e}")
            return None
    
    @trace_method("train_model")
    @time_operation("model_training")
    def _train_model(self, df: pd.DataFrame) -> Tuple[Optional[RandomForestRegressor], Optional[MinMaxScaler], Optional[List[str]]]:
        """Train the ML model and return model, scaler, and feature list"""
        try:
            # Prepare features and target
            features = ['Open', 'High', 'Low', 'Close', 'Volume', 'sma_5', 'sma_20', 'volatility']
            X = df[features].values
            y = df['Close'].shift(-1).dropna().values
            X = X[:-1]  # Remove last row as we don't have y for it
            
            # Scale features
            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_scaled, y)
            
            return model, scaler, features
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return None, None, None
    
    @trace_method("generate_predictions")
    def _generate_predictions(self, model, scaler, df: pd.DataFrame, features: List[str], 
                            end_date: date, days: int) -> List[StockPrediction]:
        """Generate predictions for the specified number of days"""
        try:
            predictions = []
            X = df[features].values
            last_data = X[-1].reshape(1, -1)
            current_date = end_date
            
            for i in range(days):
                # Scale the last data point
                last_data_scaled = scaler.transform(last_data)
                
                # Predict next day's close
                pred_close = model.predict(last_data_scaled)[0]
                
                # Add some randomness for confidence interval (simplified)
                confidence_range = pred_close * CONFIDENCE_INTERVAL_RANGE
                
                # Add to predictions
                current_date += timedelta(days=1)
                predictions.append(StockPrediction(
                    date=current_date,
                    predicted_close=pred_close,
                    confidence_interval_lower=pred_close - confidence_range,
                    confidence_interval_upper=pred_close + confidence_range
                ))
                
                # Update last_data for next prediction (using predicted close as next day's close)
                last_data = np.roll(last_data, -1)
                last_data[0, -1] = pred_close  # Update close price
                last_data[0, 0] = pred_close * (1 + np.random.normal(0, 0.01))  # Simulated open
                last_data[0, 1] = max(pred_close * (1 + abs(np.random.normal(0, 0.02))), last_data[0, 0])  # High
                last_data[0, 2] = min(pred_close * (1 - abs(np.random.normal(0, 0.02))), last_data[0, 0])  # Low
                last_data[0, 3] = pred_close  # Close
                
                # Update SMAs and other features (simplified)
                last_data[0, 5] = (last_data[0, 3] + X[-4:, 3].sum()) / 5  # SMA_5
                last_data[0, 6] = (last_data[0, 3] + X[-19:, 3].sum()) / 20  # SMA_20
                last_data[0, 7] = np.std(np.diff(np.log(np.concatenate([X[:, 3], [pred_close]])))) * np.sqrt(252)  # Volatility
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return []
    
    @trace_method("get_stock_recommendation")
    @log_method_call(include_args=True, include_result=True)
    async def get_stock_recommendation(self, ticker: str) -> Optional[StockRecommendation]:
        """
        Generate a stock recommendation based on technical indicators
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            StockRecommendation object with recommendation and confidence
        """
        try:
            # Get recent data
            end_date = date.today()
            start_date = end_date - timedelta(days=60)  # 2 months of data
            
            stocks = await self.get_stock_data(ticker, start_date, end_date)
            if stocks.empty:
                return None
            
            indicators = self._calculate_technical_indicators(stocks)
            if indicators is None:
                return None
            
            recommendation_data = self._generate_recommendation_logic(indicators, ticker, end_date)
            return recommendation_data
            
        except Exception as e:
            logger.error(f"Error generating recommendation for {ticker}: {e}")
            return None
    
    @trace_method("calculate_technical_indicators")
    def _calculate_technical_indicators(self, stocks: pd.DataFrame) -> Optional[dict]:
        """Calculate technical indicators for recommendation logic"""
        try:
            # Convert to DataFrame for analysis
            df = stocks.copy()
            df = df.sort_values('Date')
            
            # Calculate technical indicators
            df['sma_20'] = df['Close'].rolling(window=20).mean()
            df['sma_50'] = df['Close'].rolling(window=50).mean()
            df['rsi'] = self._calculate_rsi(df['Close'])
            
            # Get latest values
            latest = df.iloc[-1]
            
            # Simple recommendation logic (can be enhanced)
            if pd.isna(latest['sma_20']) or pd.isna(latest['sma_50']):
                logger.warning("Insufficient data for technical indicators")
                return None
            
            return {
                'price': latest['Close'],
                'sma_20': latest['sma_20'],
                'sma_50': latest['sma_50'],
                'rsi': latest['rsi']
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return None
    
    @trace_method("generate_recommendation_logic")
    def _generate_recommendation_logic(self, indicators: dict, ticker: str, end_date: date) -> StockRecommendation:
        """Generate recommendation based on technical indicators"""
        try:
            price = indicators['price']
            sma_20 = indicators['sma_20']
            sma_50 = indicators['sma_50']
            rsi = indicators['rsi']
            
            # Simple strategy
            buy_signals = 0
            sell_signals = 0
            
            # Moving average crossover
            if sma_20 > sma_50 and (sma_20 - sma_50) / sma_50 > 0.02:  # 2% above
                buy_signals += 1
            elif sma_20 < sma_50 and (sma_50 - sma_20) / sma_20 > 0.02:  # 2% below
                sell_signals += 1
                
            # RSI
            if rsi < 30:  # Oversold
                buy_signals += 1
            elif rsi > 70:  # Overbought
                sell_signals += 1
                
            # Price vs moving averages
            if price > sma_20 and price > sma_50:
                buy_signals += 1
            elif price < sma_20 and price < sma_50:
                sell_signals += 1
            
            # Determine final recommendation
            if buy_signals - sell_signals >= 2:
                recommendation = "BUY"
                confidence = 0.7 + min(0.29, (buy_signals - 2) * 0.1)  # 0.7 to 0.99
            elif sell_signals - buy_signals >= 2:
                recommendation = "SELL"
                confidence = 0.7 + min(0.29, (sell_signals - 2) * 0.1)  # 0.7 to 0.99
            else:
                recommendation = "HOLD"
                confidence = 0.6
                
            # Simple target price (can be enhanced)
            if recommendation == "BUY":
                target_price = price * 1.1  # 10% upside
            elif recommendation == "SELL":
                target_price = price * 0.9  # 10% downside
            else:
                target_price = price * 1.05  # 5% upside for HOLD
            
            return StockRecommendation(
                ticker=ticker,
                current_price=price,
                target_price=round(target_price, 2),
                recommendation=recommendation,
                confidence=round(confidence, 2),
                last_updated=end_date
            )
            
        except Exception as e:
            logger.error(f"Error in recommendation logic: {e}")
            raise
    
    @trace_method("calculate_rsi")
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
