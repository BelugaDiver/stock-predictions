from typing import List, Optional, Dict, Any
import pandas as pd
import yfinance as yf
from datetime import date, timedelta
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..schemas.discovery import (
    TickerSearchResult, SearchSuggestion, SectorInfo, 
    IndustryInfo, MarketCapCategory, StockSummary
)
from ..telemetry_decorators import (
    trace_method, 
    measure_yfinance_call, 
    log_method_call,
    time_operation
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

    @trace_method("batch_fetch_ticker_info")
    @measure_yfinance_call("batch")
    def _batch_fetch_ticker_info(self, tickers: List[str], max_workers: int = 10) -> Dict[str, Dict[str, Any]]:
        """
        Batch fetch ticker information using concurrent requests with chunking strategy
        """
        try:
            return self._process_ticker_chunks(tickers, max_workers)
        except Exception:
            # Final fallback to individual requests
            return self._fallback_to_individual_requests(tickers, max_workers)

    def _process_ticker_chunks(self, tickers: List[str], max_workers: int) -> Dict[str, Dict[str, Any]]:
        """Process tickers in chunks of optimal size"""
        ticker_info = {}
        ticker_chunks = self._create_ticker_chunks(tickers)
        
        for chunk in ticker_chunks:
            chunk_results = self._process_single_chunk(chunk, max_workers)
            ticker_info.update(chunk_results)
            
        return ticker_info

    def _create_ticker_chunks(self, tickers: List[str], chunk_size: int = 20) -> List[List[str]]:
        """Split tickers into optimal chunks for batch processing"""
        return [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]

    def _process_single_chunk(self, chunk: List[str], max_workers: int) -> Dict[str, Dict[str, Any]]:
        """Process a single chunk of tickers with batch download and concurrent info fetching"""
        try:
            return self._process_chunk_with_batch_download(chunk, max_workers)
        except Exception:
            # Fallback to individual requests for this chunk
            return self._process_chunk_individually(chunk, max_workers)

    def _process_chunk_with_batch_download(self, chunk: List[str], max_workers: int) -> Dict[str, Dict[str, Any]]:
        """Process chunk using batch download for price data and concurrent info fetching"""
        batch_data = self._download_chunk_price_data(chunk)
        return self._fetch_chunk_info_concurrently(chunk, batch_data, max_workers)

    @measure_yfinance_call("batch_download")
    def _download_chunk_price_data(self, chunk: List[str]):
        """Download price data for a chunk using yfinance batch download"""
        return yf.download(chunk, period="2d", group_by="ticker", auto_adjust=True, prepost=True)

    def _fetch_chunk_info_concurrently(self, chunk: List[str], batch_data, max_workers: int) -> Dict[str, Dict[str, Any]]:
        """Fetch ticker info concurrently and merge with batch price data"""
        ticker_info = {}
        
        with ThreadPoolExecutor(max_workers=min(max_workers, len(chunk))) as executor:
            future_to_ticker = {
                executor.submit(self._get_single_ticker_info, ticker): ticker 
                for ticker in chunk
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    info = future.result()
                    if info:
                        enriched_info = self._enrich_info_with_price_data(info, ticker, batch_data, chunk)
                        ticker_info[ticker] = enriched_info
                except Exception:
                    # Log but continue with other tickers
                    pass
                    
        return ticker_info

    def _enrich_info_with_price_data(self, info: Dict[str, Any], ticker: str, batch_data, chunk: List[str]) -> Dict[str, Any]:
        """Enrich ticker info with price data from batch download"""
        if batch_data.empty:
            return info
            
        ticker_data = self._extract_ticker_data_from_batch(ticker, batch_data, chunk)
        if ticker_data is not None and not ticker_data.empty:
            self._add_price_metrics_to_info(info, ticker_data)
            
        return info

    def _extract_ticker_data_from_batch(self, ticker: str, batch_data, chunk: List[str]):
        """Extract individual ticker data from batch download results"""
        if len(chunk) == 1:
            return batch_data
        else:
            return batch_data[ticker] if ticker in batch_data.columns else None

    def _add_price_metrics_to_info(self, info: Dict[str, Any], ticker_data) -> None:
        """Add price metrics (current price, change, volume) to ticker info"""
        info['current_price'] = float(ticker_data['Close'].iloc[-1])
        
        if len(ticker_data) > 1:
            prev_price = float(ticker_data['Close'].iloc[-2])
            info['price_change'] = info['current_price'] - prev_price
            info['price_change_percent'] = (info['price_change'] / prev_price) * 100
            
        if 'Volume' in ticker_data:
            info['volume'] = int(ticker_data['Volume'].iloc[-1])

    def _process_chunk_individually(self, chunk: List[str], max_workers: int) -> Dict[str, Dict[str, Any]]:
        """Fallback: process chunk using individual ticker requests"""
        ticker_info = {}
        
        with ThreadPoolExecutor(max_workers=min(max_workers, len(chunk))) as executor:
            future_to_ticker = {
                executor.submit(self._get_full_ticker_data, ticker): ticker 
                for ticker in chunk
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    info = future.result()
                    if info:
                        ticker_info[ticker] = info
                except Exception:
                    pass
                    
        return ticker_info

    def _fallback_to_individual_requests(self, tickers: List[str], max_workers: int) -> Dict[str, Dict[str, Any]]:
        """Final fallback: process all tickers individually with concurrency"""
        ticker_info = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(self._get_full_ticker_data, ticker): ticker 
                for ticker in tickers
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    info = future.result()
                    if info:
                        ticker_info[ticker] = info
                except Exception:
                    pass
                    
        return ticker_info

    @measure_yfinance_call("ticker")
    def _get_single_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get basic info for a single ticker"""
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            return info if info and 'longName' in info else None
        except:
            return None

    @measure_yfinance_call("ticker")
    def _get_full_ticker_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get full ticker data including price history"""
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            hist = ticker_obj.history(period="2d")
            
            if not info or 'longName' not in info:
                return None
                
            # Add price data from history
            if not hist.empty:
                info['current_price'] = float(hist['Close'].iloc[-1])
                info['volume'] = int(hist['Volume'].iloc[-1])
                
                if len(hist) > 1:
                    prev_price = float(hist['Close'].iloc[-2])
                    info['price_change'] = info['current_price'] - prev_price
                    info['price_change_percent'] = (info['price_change'] / prev_price) * 100
                    
            return info
        except:
            return None

    @trace_method("batch_create_ticker_results")
    def _batch_create_ticker_results(self, ticker_info_dict: Dict[str, Dict[str, Any]]) -> List[TickerSearchResult]:
        """Create TickerSearchResult objects from batch fetched data"""
        results = []
        
        for ticker, info in ticker_info_dict.items():
            try:
                result = TickerSearchResult(
                    ticker=ticker,
                    company_name=info.get('longName', ticker),
                    sector=info.get('sector'),
                    industry=info.get('industry'),
                    market_cap=info.get('marketCap'),
                    current_price=info.get('current_price'),
                    price_change=info.get('price_change'),
                    price_change_percent=info.get('price_change_percent'),
                    volume=info.get('volume'),
                    exchange=info.get('exchange')
                )
                results.append(result)
            except Exception:
                # Skip invalid data
                continue
                
        return results

    @trace_method("batch_create_stock_summaries")
    def _batch_create_stock_summaries(self, ticker_info_dict: Dict[str, Dict[str, Any]]) -> List[StockSummary]:
        """Create StockSummary objects from batch fetched data"""
        summaries = []
        
        for ticker, info in ticker_info_dict.items():
            try:
                summary = StockSummary(
                    ticker=ticker,
                    company_name=info.get('longName', ticker),
                    current_price=info.get('current_price'),
                    price_change=info.get('price_change'),
                    price_change_percent=info.get('price_change_percent'),
                    volume=info.get('volume'),
                    market_cap=info.get('marketCap'),
                    sector=info.get('sector'),
                    industry=info.get('industry')
                )
                summaries.append(summary)
            except Exception:
                # Skip invalid data
                continue
                
        return summaries

    @trace_method("search_tickers")
    @log_method_call(include_args=True, include_result=True)
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
        query_upper = query.upper()
        
        # Find matching tickers first (without API calls)
        matching_tickers = []
        
        # Check for exact match
        if query_upper in self.popular_tickers:
            matching_tickers.append(query_upper)
        
        # Find partial matches in popular tickers
        for ticker in self.popular_tickers:
            if ticker != query_upper and (
                ticker.startswith(query_upper) or 
                query_upper in ticker
            ):
                matching_tickers.append(ticker)
                if len(matching_tickers) >= limit * 2:  # Get extra to filter later
                    break
        
        # Batch fetch ticker information
        if matching_tickers:
            ticker_info_dict = self._batch_fetch_ticker_info(matching_tickers[:limit * 2])
            
            # Filter by company name if needed and create results
            results = []
            for ticker in matching_tickers:
                if len(results) >= limit:
                    break
                    
                if ticker in ticker_info_dict:
                    info = ticker_info_dict[ticker]
                    company_name = info.get('longName', '')
                    
                    # Check if query matches ticker or company name
                    if (query_upper in ticker or 
                        ticker.startswith(query_upper) or
                        query.upper() in company_name.upper()):
                        
                        result = TickerSearchResult(
                            ticker=ticker,
                            company_name=company_name,
                            sector=info.get('sector'),
                            industry=info.get('industry'),
                            market_cap=info.get('marketCap'),
                            current_price=info.get('current_price'),
                            price_change=info.get('price_change'),
                            price_change_percent=info.get('price_change_percent'),
                            volume=info.get('volume'),
                            exchange=info.get('exchange')
                        )
                        results.append(result)
            
            return results
        
        return []

    @trace_method("try_exact_ticker_match") 
    @measure_yfinance_call("ticker")
    def _try_exact_ticker_match(self, ticker: str) -> Optional[TickerSearchResult]:
        """Try to get exact ticker match"""
        try:
            ticker_info = yf.Ticker(ticker)
            info = ticker_info.info
            if info and 'longName' in info:
                return self._create_ticker_result(ticker, info)
        except:
            pass
        return None

    @trace_method("search_popular_tickers")
    def _search_popular_tickers(self, query: str, query_upper: str, limit: int, existing_results: List) -> List[TickerSearchResult]:
        """Search through popular tickers"""
        results = []
        
        for ticker in self.popular_tickers:
            if len(existing_results) + len(results) >= limit:
                break
                
            # Skip if already added
            if any(r.ticker == ticker for r in existing_results):
                continue
                
            # Check if ticker matches query
            if (query_upper in ticker or 
                ticker.startswith(query_upper) or
                self._company_name_matches(ticker, query)):
                
                ticker_result = self._get_ticker_info_safe(ticker)
                if ticker_result:
                    results.append(ticker_result)
        
        return results

    @measure_yfinance_call("ticker")
    def _get_ticker_info_safe(self, ticker: str) -> Optional[TickerSearchResult]:
        """Safely get ticker info with error handling"""
        try:
            ticker_info = yf.Ticker(ticker)
            info = ticker_info.info
            if info and 'longName' in info:
                return self._create_ticker_result(ticker, info)
        except:
            pass
        return None

    @trace_method("get_search_suggestions")
    def get_search_suggestions(self, query: str, limit: int = 10) -> List[SearchSuggestion]:
        """
        Get search suggestions for autocomplete
        """
        query_upper = query.upper()
        
        # Find matching tickers first
        matching_tickers = []
        for ticker in self.popular_tickers:
            if (query_upper in ticker or 
                ticker.startswith(query_upper)):
                matching_tickers.append(ticker)
                if len(matching_tickers) >= limit * 2:
                    break
        
        # Batch fetch basic info
        if matching_tickers:
            ticker_info_dict = self._batch_fetch_ticker_info(matching_tickers[:limit * 2])
            
            suggestions = []
            for ticker in matching_tickers:
                if len(suggestions) >= limit:
                    break
                    
                if ticker in ticker_info_dict:
                    info = ticker_info_dict[ticker]
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
            
            return suggestions
        
        return []

    @measure_yfinance_call("ticker")
    def _create_suggestion_safe(self, ticker: str, query: str, query_upper: str) -> Optional[SearchSuggestion]:
        """Safely create suggestion with error handling"""
        try:
            ticker_info = yf.Ticker(ticker)
            info = ticker_info.info
            
            if not info or 'longName' not in info:
                return None
                
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
                return None
                
            return SearchSuggestion(
                ticker=ticker,
                company_name=company_name,
                match_type=match_type
            )
        except:
            return None

    @trace_method("get_sectors")
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

    @trace_method("get_sector_stocks")
    def get_sector_stocks(self, sector: str, limit: int = 50) -> List[StockSummary]:
        """
        Get stocks within a specific sector using enhanced yfinance Sector API integration
        """
        try:
            # Use the enhanced method which tries yfinance.Sector() API first, then falls back
            sector_tickers = self._get_enhanced_tickers_by_sector(sector)[:limit]
            
            if sector_tickers:
                # Batch fetch all ticker information
                ticker_info_dict = self._batch_fetch_ticker_info(sector_tickers)
                
                # Filter results to ensure they actually belong to the sector
                filtered_summaries = []
                for summary in self._batch_create_stock_summaries(ticker_info_dict):
                    # More flexible sector validation
                    if (summary.sector and (
                        sector.lower() in summary.sector.lower() or
                        summary.sector.lower() in sector.lower() or
                        sector in ["Technology", "Healthcare", "Financial Services", 
                                 "Consumer Cyclical", "Consumer Defensive", "Energy", 
                                 "Materials", "Real Estate", "Communication Services", 
                                 "Industrials", "Utilities"]  # Accept our standard sectors
                    )) or len(filtered_summaries) < limit // 2:  # Allow some flexibility
                        filtered_summaries.append(summary)
                        
                return filtered_summaries[:limit]
        
        except Exception:
            # Fallback to original implementation
            sector_tickers = self._get_tickers_by_sector(sector)[:limit]
            
            if sector_tickers:
                ticker_info_dict = self._batch_fetch_ticker_info(sector_tickers)
                return self._batch_create_stock_summaries(ticker_info_dict)
        
        return []

    @trace_method("get_industries")
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

    @trace_method("get_industry_stocks")
    def get_industry_stocks(self, industry: str, limit: int = 50) -> List[StockSummary]:
        """
        Get stocks within specific industry
        """
        # For demo, return subset of popular stocks
        # In real implementation, filter by actual industry classification
        tickers = self.popular_tickers[:limit]
        
        if tickers:
            # Batch fetch all ticker information
            ticker_info_dict = self._batch_fetch_ticker_info(tickers)
            
            # Create stock summaries from batch data
            return self._batch_create_stock_summaries(ticker_info_dict)
        
        return []

    @trace_method("get_stocks_by_market_cap")
    def get_stocks_by_market_cap(self, category: str, limit: int = 100) -> List[StockSummary]:
        """
        Get stocks by market capitalization category using comprehensive ticker screening
        """
        # Define market cap ranges (in billions)
        cap_ranges = {
            "large-cap": (10, None),      # >$10B
            "mid-cap": (2, 10),           # $2B-$10B
            "small-cap": (0.3, 2),        # $300M-$2B
            "micro-cap": (0, 0.3)         # <$300M
        }
        
        min_cap, max_cap = cap_ranges.get(category, (0, None))
        
        # Get a more comprehensive list of tickers for screening
        candidate_tickers = self._get_comprehensive_ticker_list(limit * 3)  # Get 3x to filter down
        
        # Batch fetch ticker information
        ticker_info_dict = self._batch_fetch_ticker_info(candidate_tickers)
        
        # Filter by market cap and create summaries
        stocks = []
        sorted_tickers = []
        
        # First, collect and sort by market cap
        for ticker, info in ticker_info_dict.items():
            market_cap = info.get('marketCap')
            if market_cap and info.get('current_price'):  # Ensure we have both market cap and price
                market_cap_b = market_cap / 1e9  # Convert to billions
                
                # Check if within range
                if market_cap_b >= min_cap and (max_cap is None or market_cap_b <= max_cap):
                    sorted_tickers.append((ticker, market_cap_b, info))
        
        # Sort by market cap (descending for large-cap, ascending for others)
        if category == "large-cap":
            sorted_tickers.sort(key=lambda x: x[1], reverse=True)
        else:
            sorted_tickers.sort(key=lambda x: x[1], reverse=False)
        
        # Create summaries from sorted list
        for ticker, market_cap_b, info in sorted_tickers[:limit]:
            try:
                summary = StockSummary(
                    ticker=ticker,
                    company_name=info.get('longName', ticker),
                    current_price=info.get('current_price'),
                    price_change=info.get('price_change'),
                    price_change_percent=info.get('price_change_percent'),
                    volume=info.get('volume'),
                    market_cap=info.get('marketCap'),
                    sector=info.get('sector'),
                    industry=info.get('industry')
                )
                stocks.append(summary)
            except Exception:
                continue
                
        return stocks

    @trace_method("get_stocks_by_price_range")
    def get_stocks_by_price_range(
        self, 
        min_price: float = 0, 
        max_price: float = 1000, 
        limit: int = 100
    ) -> List[StockSummary]:
        """
        Get stocks within specific price range using comprehensive ticker screening
        """
        # Get a comprehensive list of tickers for screening
        candidate_tickers = self._get_comprehensive_ticker_list(limit * 4)  # Get 4x to filter down
        
        # Batch fetch ticker information
        ticker_info_dict = self._batch_fetch_ticker_info(candidate_tickers)
        
        # Filter by price range and create summaries
        stocks = []
        price_filtered_tickers = []
        
        # First pass: filter by price and collect volume data for sorting
        for ticker, info in ticker_info_dict.items():
            current_price = info.get('current_price')
            volume = info.get('volume', 0)
            
            if (current_price and min_price <= current_price <= max_price and 
                info.get('longName') and volume > 0):  # Ensure valid data
                price_filtered_tickers.append((ticker, current_price, volume, info))
        
        # Sort by volume (descending) to get most liquid stocks first
        price_filtered_tickers.sort(key=lambda x: x[2], reverse=True)
        
        # Create summaries from sorted and filtered list
        for ticker, current_price, volume, info in price_filtered_tickers[:limit]:
            try:
                summary = StockSummary(
                    ticker=ticker,
                    company_name=info.get('longName', ticker),
                    current_price=current_price,
                    price_change=info.get('price_change'),
                    price_change_percent=info.get('price_change_percent'),
                    volume=volume,
                    market_cap=info.get('marketCap'),
                    sector=info.get('sector'),
                    industry=info.get('industry')
                )
                stocks.append(summary)
            except Exception:
                continue
                
        return stocks

    def _get_stock_summary_safe(self, ticker: str) -> Optional[StockSummary]:
        """Get stock summary with error handling"""
        try:
            return self._get_stock_summary(ticker)
        except:
            return None

    @trace_method("create_ticker_result")
    @measure_yfinance_call("ticker")
    def _create_ticker_result(self, ticker: str, info: Dict[str, Any]) -> TickerSearchResult:
        """
        Create TickerSearchResult from yfinance info
        """
        # Get current price data
        current_price, price_change, price_change_percent = self._get_price_data(ticker, info)

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

    @measure_yfinance_call("ticker")
    def _get_price_data(self, ticker: str, info: Dict[str, Any]) -> tuple:
        """Get current price data for ticker"""
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
            
        return current_price, price_change, price_change_percent

    @measure_yfinance_call("ticker")
    def _get_stock_summary(self, ticker: str) -> Optional[StockSummary]:
        """
        Get stock summary data
        """
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

    @measure_yfinance_call("ticker")
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

    def _get_enhanced_tickers_by_sector(self, sector: str) -> List[str]:
        """
        Get enhanced ticker list by sector using yfinance.Sector() API for real-time data
        """
        # Map our sector names to yfinance sector keys
        sector_key_mapping = self._get_yfinance_sector_key(sector)
        
        if sector_key_mapping:
            try:
                # Use yfinance Sector API to get real-time top companies
                sector_obj = yf.Sector(sector_key_mapping)
                top_companies_df = sector_obj.top_companies
                
                if not top_companies_df.empty:
                    # Extract ticker symbols from the DataFrame index or symbol column
                    if hasattr(top_companies_df, 'index'):
                        tickers = list(top_companies_df.index)
                    elif 'Symbol' in top_companies_df.columns:
                        tickers = list(top_companies_df['Symbol'])
                    elif 'symbol' in top_companies_df.columns:
                        tickers = list(top_companies_df['symbol'])
                    else:
                        # Try to get the first column that looks like ticker symbols
                        tickers = list(top_companies_df.iloc[:, 0])
                    
                    # Clean and validate tickers
                    valid_tickers = []
                    for ticker in tickers:
                        if isinstance(ticker, str) and ticker.strip():
                            # Clean ticker symbol
                            clean_ticker = ticker.strip().upper()
                            # Basic validation - should be mostly letters and maybe dots/dashes
                            if len(clean_ticker) <= 6 and clean_ticker.replace('.', '').replace('-', '').isalpha():
                                valid_tickers.append(clean_ticker)
                    
                    if valid_tickers:
                        return valid_tickers[:50]  # Limit to top 50 companies
            except Exception:
                # If API fails, return basic popular tickers for this sector
                pass
        
        # Final fallback to popular tickers if sector not found or API fails
        return self.popular_tickers[:20]

    def _get_yfinance_sector_key(self, sector: str) -> str:
        """
        Map our sector names to yfinance sector keys
        """
        sector_key_mapping = {
            "Technology": "technology",
            "Healthcare": "healthcare", 
            "Financial Services": "financial-services",
            "Consumer Cyclical": "consumer-cyclical",
            "Consumer Defensive": "consumer-defensive",
            "Industrials": "industrials",
            "Energy": "energy",
            "Materials": "basic-materials",  # Note: yfinance uses "basic-materials"
            "Real Estate": "real-estate",
            "Communication Services": "communication-services",
            "Utilities": "utilities"
        }
        
        return sector_key_mapping.get(sector)

    def _get_comprehensive_ticker_list(self, target_count: int = 300) -> List[str]:
        """
        Get a comprehensive list of tickers for screening by combining multiple sources
        """
        comprehensive_tickers = set()
        
        # Start with popular tickers
        comprehensive_tickers.update(self.popular_tickers)
        
        # Add tickers from all sectors
        for sector_tickers in self._get_all_enhanced_sector_tickers().values():
            comprehensive_tickers.update(sector_tickers)
        
        # Add some additional high-volume/high-market-cap tickers
        additional_tickers = [
            # Additional large caps
            "TSMC", "ASML", "ROCHE", "NESN", "SAP", "TM", "NVO", "UL", "BABA", "TSM",
            # Additional mid caps that are commonly traded
            "ROKU", "TWLO", "ZM", "PTON", "UBER", "LYFT", "SHOP", "SQ", "DKNG", "RBLX",
            # REITs and utilities
            "SPY", "QQQ", "IWM", "VTI", "EFA", "EEM", "GLD", "SLV", "USO", "XLE",
            # Additional growth stocks
            "ARKK", "ARKQ", "ARKG", "MSTR", "COIN", "HOOD", "SOFI", "AFRM", "BNPL", "OPEN"
        ]
        comprehensive_tickers.update(additional_tickers)
        
        # Convert to list and return up to target count
        ticker_list = list(comprehensive_tickers)
        
        # Prioritize by putting popular tickers first
        prioritized_list = []
        prioritized_list.extend([t for t in self.popular_tickers if t in ticker_list])
        prioritized_list.extend([t for t in ticker_list if t not in self.popular_tickers])
        
        return prioritized_list[:target_count]

    def _get_all_enhanced_sector_tickers(self) -> Dict[str, List[str]]:
        """
        Get all enhanced sector ticker mappings
        """
        return {
            sector: self._get_enhanced_tickers_by_sector(sector) 
            for sector in self.sector_industry_mapping.keys()
        }
