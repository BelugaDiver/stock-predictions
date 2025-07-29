from typing import List, Optional, Dict, Any
import pandas as pd
import yfinance as yf
from datetime import date, timedelta
import re
from ..schemas.discovery import (
    TickerSearchResult, SearchSuggestion, SectorInfo, 
    IndustryInfo, MarketCapCategory, StockSummary
)

class DiscoveryService:
    def __init__(self):
        # Static sector-industry mapping (can be moved to database later)
        self.sector_industry_mapping = {
            "Technology": [
                "Software", "Hardware", "Semiconductors", "Internet Services",
                "IT Services", "Computer Systems", "Electronic Components"
            ],
            "Healthcare": [
                "Pharmaceuticals", "Biotechnology", "Medical Devices", 
                "Healthcare Services", "Health Insurance"
            ],
            "Financial Services": [
                "Banks", "Insurance", "Investment Banking", "Asset Management",
                "Credit Services", "Real Estate"
            ],
            "Consumer Cyclical": [
                "Retail", "Automotive", "Airlines", "Hotels & Restaurants",
                "Media & Entertainment", "Apparel"
            ],
            "Consumer Defensive": [
                "Food & Beverages", "Household Products", "Personal Care",
                "Discount Stores", "Grocery Stores"
            ],
            "Industrials": [
                "Aerospace & Defense", "Manufacturing", "Transportation",
                "Construction", "Industrial Equipment"
            ],
            "Energy": [
                "Oil & Gas", "Renewable Energy", "Utilities", "Coal"
            ],
            "Materials": [
                "Metals & Mining", "Chemicals", "Construction Materials",
                "Paper & Packaging"
            ],
            "Real Estate": [
                "REITs", "Real Estate Development", "Real Estate Services"
            ],
            "Communication Services": [
                "Telecommunications", "Media", "Internet Services"
            ],
            "Utilities": [
                "Electric Utilities", "Gas Utilities", "Water Utilities",
                "Renewable Utilities"
            ]
        }
        
        # Popular tickers for quick search (can be expanded)
        self.popular_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
            "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "ADBE", "CRM",
            "PYPL", "INTC", "CMCSA", "PFE", "VZ", "KO", "PEP", "T", "ABT",
            "CSCO", "AVGO", "TMO", "ACN", "TXN", "LLY", "ABBV", "COST", "WMT"
        ]

    def search_tickers(
        self, 
        query: str, 
        limit: int = 20, 
        include_delisted: bool = False,
        market: Optional[str] = None
    ) -> List[TickerSearchResult]:
        """
        Search for tickers by symbol or company name
        """
        results = []
        query_upper = query.upper()
        
        # First, try exact ticker match
        try:
            ticker_info = yf.Ticker(query_upper)
            info = ticker_info.info
            if info and 'longName' in info:
                results.append(self._create_ticker_result(query_upper, info))
        except:
            pass
        
        # Search through popular tickers
        for ticker in self.popular_tickers:
            if len(results) >= limit:
                break
                
            # Skip if already added
            if any(r.ticker == ticker for r in results):
                continue
                
            # Check if ticker matches query
            if (query_upper in ticker or 
                ticker.startswith(query_upper) or
                self._company_name_matches(ticker, query)):
                
                try:
                    ticker_info = yf.Ticker(ticker)
                    info = ticker_info.info
                    if info and 'longName' in info:
                        results.append(self._create_ticker_result(ticker, info))
                except:
                    continue
        
        return results[:limit]

    def get_search_suggestions(self, query: str, limit: int = 10) -> List[SearchSuggestion]:
        """
        Get search suggestions for autocomplete
        """
        suggestions = []
        query_upper = query.upper()
        
        for ticker in self.popular_tickers:
            if len(suggestions) >= limit:
                break
                
            try:
                ticker_info = yf.Ticker(ticker)
                info = ticker_info.info
                
                if not info or 'longName' not in info:
                    continue
                    
                company_name = info.get('longName', '')
                
                # Determine match type
                match_type = "partial"
                if ticker == query_upper:
                    match_type = "ticker"
                elif ticker.startswith(query_upper):
                    match_type = "ticker"
                elif company_name.upper().startswith(query.upper()):
                    match_type = "name"
                elif query.upper() in company_name.upper():
                    match_type = "name"
                else:
                    continue
                    
                suggestions.append(SearchSuggestion(
                    ticker=ticker,
                    company_name=company_name,
                    match_type=match_type
                ))
            except:
                continue
                
        return suggestions

    def get_sectors(self) -> List[SectorInfo]:
        """
        Get all available sectors with stock counts
        """
        sectors = []
        for sector_name, industries in self.sector_industry_mapping.items():
            # Estimate stock count (in real implementation, query database)
            stock_count = len(industries) * 15  # Rough estimate
            
            sectors.append(SectorInfo(
                name=sector_name,
                stock_count=stock_count,
                description=f"Companies in the {sector_name.lower()} sector"
            ))
        
        return sectors

    def get_sector_stocks(self, sector: str, limit: int = 50) -> List[StockSummary]:
        """
        Get stocks within a specific sector
        """
        # For demo, return relevant stocks from popular list
        sector_tickers = self._get_tickers_by_sector(sector)
        stocks = []
        
        for ticker in sector_tickers[:limit]:
            try:
                stock_data = self._get_stock_summary(ticker)
                if stock_data:
                    stocks.append(stock_data)
            except:
                continue
                
        return stocks

    def get_industries(self, sector: Optional[str] = None) -> List[IndustryInfo]:
        """
        Get industries, optionally filtered by sector
        """
        industries = []
        
        if sector:
            # Get industries for specific sector
            sector_industries = self.sector_industry_mapping.get(sector, [])
            for industry in sector_industries:
                industries.append(IndustryInfo(
                    name=industry,
                    sector=sector,
                    stock_count=20,  # Estimate
                    description=f"Companies in {industry}"
                ))
        else:
            # Get all industries
            for sector_name, industry_list in self.sector_industry_mapping.items():
                for industry in industry_list:
                    industries.append(IndustryInfo(
                        name=industry,
                        sector=sector_name,
                        stock_count=20,  # Estimate
                        description=f"Companies in {industry}"
                    ))
        
        return industries

    def get_industry_stocks(self, industry: str, limit: int = 50) -> List[StockSummary]:
        """
        Get stocks within specific industry
        """
        # For demo, return subset of popular stocks
        # In real implementation, filter by actual industry classification
        tickers = self.popular_tickers[:limit]
        stocks = []
        
        for ticker in tickers:
            try:
                stock_data = self._get_stock_summary(ticker)
                if stock_data:
                    stocks.append(stock_data)
            except:
                continue
                
        return stocks

    def get_stocks_by_market_cap(self, category: str, limit: int = 100) -> List[StockSummary]:
        """
        Get stocks by market capitalization category
        """
        # Define market cap ranges (in billions)
        cap_ranges = {
            "large-cap": (10, None),      # >$10B
            "mid-cap": (2, 10),           # $2B-$10B
            "small-cap": (0.3, 2),        # $300M-$2B
            "micro-cap": (0, 0.3)         # <$300M
        }
        
        min_cap, max_cap = cap_ranges.get(category, (0, None))
        stocks = []
        
        for ticker in self.popular_tickers:
            if len(stocks) >= limit:
                break
                
            try:
                stock_data = self._get_stock_summary(ticker)
                if stock_data and stock_data.market_cap:
                    market_cap_b = stock_data.market_cap / 1e9  # Convert to billions
                    
                    # Check if within range
                    if market_cap_b >= min_cap and (max_cap is None or market_cap_b <= max_cap):
                        stocks.append(stock_data)
            except:
                continue
                
        return stocks

    def get_stocks_by_price_range(
        self, 
        min_price: float = 0, 
        max_price: float = 1000, 
        limit: int = 100
    ) -> List[StockSummary]:
        """
        Get stocks within specific price range
        """
        stocks = []
        
        for ticker in self.popular_tickers:
            if len(stocks) >= limit:
                break
                
            try:
                stock_data = self._get_stock_summary(ticker)
                if (stock_data and 
                    min_price <= stock_data.current_price <= max_price):
                    stocks.append(stock_data)
            except:
                continue
                
        return stocks

    def _create_ticker_result(self, ticker: str, info: Dict[str, Any]) -> TickerSearchResult:
        """
        Create TickerSearchResult from yfinance info
        """
        # Get current price data
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period="2d")
            
            current_price = None
            price_change = None
            price_change_percent = None
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                if len(hist) > 1:
                    prev_price = float(hist['Close'].iloc[-2])
                    price_change = current_price - prev_price
                    price_change_percent = (price_change / prev_price) * 100
                    
        except:
            current_price = info.get('currentPrice')
            price_change = info.get('change')
            price_change_percent = info.get('changePercent')

        return TickerSearchResult(
            ticker=ticker,
            company_name=info.get('longName', ticker),
            sector=info.get('sector'),
            industry=info.get('industry'),
            market_cap=info.get('marketCap'),
            current_price=current_price,
            price_change=price_change,
            price_change_percent=price_change_percent,
            volume=info.get('volume'),
            exchange=info.get('exchange')
        )

    def _get_stock_summary(self, ticker: str) -> Optional[StockSummary]:
        """
        Get stock summary data
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            hist = ticker_obj.history(period="2d")
            
            if hist.empty or not info or 'longName' not in info:
                return None
                
            current_price = float(hist['Close'].iloc[-1])
            volume = int(hist['Volume'].iloc[-1])
            
            price_change = 0
            price_change_percent = 0
            
            if len(hist) > 1:
                prev_price = float(hist['Close'].iloc[-2])
                price_change = current_price - prev_price
                price_change_percent = (price_change / prev_price) * 100
            
            return StockSummary(
                ticker=ticker,
                company_name=info.get('longName', ticker),
                current_price=current_price,
                price_change=price_change,
                price_change_percent=price_change_percent,
                volume=volume,
                market_cap=info.get('marketCap'),
                sector=info.get('sector'),
                industry=info.get('industry')
            )
        except:
            return None

    def _company_name_matches(self, ticker: str, query: str) -> bool:
        """
        Check if company name matches query
        """
        try:
            ticker_info = yf.Ticker(ticker)
            info = ticker_info.info
            company_name = info.get('longName', '')
            return query.upper() in company_name.upper()
        except:
            return False

    def _get_tickers_by_sector(self, sector: str) -> List[str]:
        """
        Get tickers that belong to a specific sector
        This is a simplified implementation - in production, use proper sector classification
        """
        sector_mappings = {
            "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "ADBE", "CRM", "INTC", "CSCO", "AVGO", "TXN"],
            "Healthcare": ["JNJ", "PFE", "ABT", "TMO", "LLY", "ABBV"],
            "Financial Services": ["JPM", "V", "MA", "PYPL"],
            "Consumer Cyclical": ["AMZN", "TSLA", "HD", "DIS", "COST"],
            "Consumer Defensive": ["PG", "KO", "PEP", "WMT"],
            "Communication Services": ["META", "NFLX", "CMCSA", "VZ", "T"],
            "Energy": [],
            "Industrials": [],
            "Materials": [],
            "Real Estate": [],
            "Utilities": []
        }
        
        return sector_mappings.get(sector, self.popular_tickers[:10])
