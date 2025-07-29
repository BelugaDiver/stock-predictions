from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from ..models.daily import Daily
from ..schemas.stock import Stock, StockPredictionRequest, StockPrediction, StockRecommendation
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf

class StockService:
    def __init__(self):
        pass
    
    def get_stock_data(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        """Retrieve stock data for a given ticker and date range using Yahoo Finance, returns a DataFrame"""
        df = yf.download(ticker, start=start_date, end=end_date + timedelta(days=1), progress=False)
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        df['Ticker'] = ticker
        return df
    
    def predict_stock_price(
        self, 
        ticker: str, 
        days: int = 7,
        lookback_days: int = 90
    ) -> List[StockPrediction]:
        """
        Predict stock prices for the next 'days' days
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to predict
            lookback_days: Number of historical days to use for prediction
            
        Returns:
            List of StockPrediction objects with date and predicted close price
        """
        # Get historical data
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days)
        
        stocks = self.get_stock_data(ticker, start_date, end_date)
        if stocks.empty:
            return []
        
        # Prepare data for ML model
        df = stocks.copy()
        df = df.sort_values('Date')
        
        # Feature engineering
        df['returns'] = df['Close'].pct_change()
        df['sma_5'] = df['Close'].rolling(window=5).mean()
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
        df = df.dropna()
        
        if len(df) < 30:  # Not enough data
            return []
        
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
        
        # Make predictions
        predictions = []
        last_data = X[-1].reshape(1, -1)
        current_date = end_date
        
        for _ in range(days):
            # Scale the last data point
            last_data_scaled = scaler.transform(last_data)
            
            # Predict next day's close
            pred_close = model.predict(last_data_scaled)[0]
            
            # Add some randomness for confidence interval (simplified)
            confidence_range = pred_close * 0.02  # 2% range
            
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
    
    def get_stock_recommendation(self, ticker: str) -> Optional[StockRecommendation]:
        """
        Generate a stock recommendation based on technical indicators
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            StockRecommendation object with recommendation and confidence
        """
        # Get recent data
        end_date = date.today()
        start_date = end_date - timedelta(days=60)  # 2 months of data
        
        stocks = self.get_stock_data(ticker, start_date, end_date)
        if stocks.empty:
            return None
            
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
        if pd.isna(latest['sma_20']).any() or pd.isna(latest['sma_50']).any():
            return None
            
        # Determine recommendation
        price = latest['Close']
        sma_20 = latest['sma_20']
        sma_50 = latest['sma_50']
        rsi = latest['rsi']
        
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
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))
