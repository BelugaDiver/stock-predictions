from datetime import date
from pydantic import BaseModel, Field
from typing import Optional, List

class TickerSearchResult(BaseModel):
    """Individual ticker search result"""
    ticker: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    current_price: Optional[float] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    volume: Optional[int] = None
    exchange: Optional[str] = None

class SearchSuggestion(BaseModel):
    """Search suggestion for autocomplete"""
    ticker: str
    company_name: str
    match_type: str  # "ticker", "name", "partial"

class SectorInfo(BaseModel):
    """Sector information with stock count"""
    name: str
    stock_count: int
    description: Optional[str] = None

class IndustryInfo(BaseModel):
    """Industry information"""
    name: str
    sector: str
    stock_count: int
    description: Optional[str] = None

class MarketCapCategory(BaseModel):
    """Market cap category definition"""
    category: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str
    stock_count: int

class StockSummary(BaseModel):
    """Brief stock summary for browsing"""
    ticker: str
    company_name: str
    current_price: float
    price_change: float
    price_change_percent: float
    volume: int
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
