from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..schemas.discovery import (
    TickerSearchResult, SearchSuggestion, SectorInfo, 
    IndustryInfo, StockSummary
)
from ..services.discovery_service import DiscoveryService

router = APIRouter(
    prefix="/discovery",
    tags=["discovery"],
    responses={404: {"description": "Not found"}},
)

@router.get("/search", response_model=List[TickerSearchResult])
async def search_tickers(
    query: str = Query(..., description="Search query for ticker symbol or company name"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    include_delisted: bool = Query(False, description="Include delisted stocks"),
    market: Optional[str] = Query(None, description="Filter by market (NYSE, NASDAQ, AMEX)")
):
    """
    Universal search for stocks by ticker symbol or company name.
    
    - **query**: Search term (ticker symbol like 'AAPL' or company name like 'Apple')
    - **limit**: Maximum number of results to return (1-100, default: 20)
    - **include_delisted**: Whether to include delisted stocks (default: False)
    - **market**: Filter by specific market (NYSE, NASDAQ, AMEX)
    
    Returns list of matching stocks with basic information.
    """
    if len(query.strip()) < 1:
        raise HTTPException(status_code=400, detail="Query must be at least 1 character long")
    
    discovery_service = DiscoveryService()
    results = discovery_service.search_tickers(
        query=query.strip(),
        limit=limit,
        include_delisted=include_delisted,
        market=market
    )
    
    if not results:
        raise HTTPException(
            status_code=404, 
            detail=f"No stocks found matching '{query}'"
        )
    
    return results

@router.get("/search/suggestions", response_model=List[SearchSuggestion])
async def get_search_suggestions(
    query: str = Query(..., description="Partial search query for autocomplete"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions")
):
    """
    Get search suggestions for autocomplete functionality.
    
    - **query**: Partial search term for autocomplete
    - **limit**: Maximum number of suggestions (1-20, default: 10)
    
    Returns quick suggestions for UI autocomplete.
    """
    if len(query.strip()) < 1:
        return []
    
    discovery_service = DiscoveryService()
    suggestions = discovery_service.get_search_suggestions(
        query=query.strip(),
        limit=limit
    )
    
    return suggestions

@router.get("/browse/sectors", response_model=List[SectorInfo])
async def get_sectors():
    """
    Get all available sectors with stock counts.
    
    Returns list of market sectors like Technology, Healthcare, Finance, etc.
    Each sector includes the number of stocks available.
    """
    discovery_service = DiscoveryService()
    sectors = discovery_service.get_sectors()
    return sectors

@router.get("/browse/sectors/{sector}", response_model=List[StockSummary])
async def get_sector_stocks(
    sector: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of stocks to return")
):
    """
    Get stocks within a specific sector.
    
    - **sector**: Sector name (e.g., 'Technology', 'Healthcare', 'Financial Services')
    - **limit**: Maximum number of stocks (1-200, default: 50)
    
    Returns stocks sorted by market cap or volume.
    """
    discovery_service = DiscoveryService()
    stocks = discovery_service.get_sector_stocks(sector, limit)
    
    if not stocks:
        raise HTTPException(
            status_code=404,
            detail=f"No stocks found in sector '{sector}'"
        )
    
    return stocks

@router.get("/browse/industries", response_model=List[IndustryInfo])
async def get_industries(
    sector: Optional[str] = Query(None, description="Filter industries by sector")
):
    """
    Get available industries, optionally filtered by sector.
    
    - **sector**: Optional sector filter (e.g., 'Technology', 'Healthcare')
    
    Returns list of industries like Software, Biotechnology, Banking, etc.
    """
    discovery_service = DiscoveryService()
    industries = discovery_service.get_industries(sector)
    return industries

@router.get("/browse/industries/{industry}", response_model=List[StockSummary])
async def get_industry_stocks(
    industry: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of stocks to return")
):
    """
    Get stocks within a specific industry.
    
    - **industry**: Industry name (e.g., 'Software', 'Biotechnology', 'Banking')
    - **limit**: Maximum number of stocks (1-200, default: 50)
    
    Returns stocks in the specified industry.
    """
    discovery_service = DiscoveryService()
    stocks = discovery_service.get_industry_stocks(industry, limit)
    
    if not stocks:
        raise HTTPException(
            status_code=404,
            detail=f"No stocks found in industry '{industry}'"
        )
    
    return stocks

@router.get("/browse/market-cap/{category}", response_model=List[StockSummary])
async def get_stocks_by_market_cap(
    category: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of stocks to return")
):
    """
    Get stocks by market capitalization category.
    
    - **category**: Market cap category
        - `large-cap`: Market cap > $10 billion
        - `mid-cap`: Market cap $2B - $10B
        - `small-cap`: Market cap $300M - $2B  
        - `micro-cap`: Market cap < $300M
    - **limit**: Maximum number of stocks (1-500, default: 100)
    
    Returns stocks within the specified market cap range.
    """
    valid_categories = ["large-cap", "mid-cap", "small-cap", "micro-cap"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    discovery_service = DiscoveryService()
    stocks = discovery_service.get_stocks_by_market_cap(category, limit)
    
    if not stocks:
        raise HTTPException(
            status_code=404,
            detail=f"No stocks found in {category} category"
        )
    
    return stocks

@router.get("/browse/price-range", response_model=List[StockSummary])
async def get_stocks_by_price_range(
    min_price: float = Query(0, ge=0, description="Minimum stock price"),
    max_price: float = Query(1000, ge=0, description="Maximum stock price"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of stocks to return")
):
    """
    Get stocks within a specific price range.
    
    - **min_price**: Minimum stock price (default: $0)
    - **max_price**: Maximum stock price (default: $1000)
    - **limit**: Maximum number of stocks (1-500, default: 100)
    
    Returns stocks within the specified price range.
    """
    if min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price cannot be greater than max_price"
        )
    
    discovery_service = DiscoveryService()
    stocks = discovery_service.get_stocks_by_price_range(min_price, max_price, limit)
    
    if not stocks:
        raise HTTPException(
            status_code=404,
            detail=f"No stocks found in price range ${min_price:.2f} - ${max_price:.2f}"
        )
    
    return stocks
