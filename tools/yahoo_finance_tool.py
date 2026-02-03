from langchain.tools import tool
import yfinance as yf
import json


@tool
def get_yahoo_stock_data(symbol: str, function: str = "info") -> str:
    """
    Fetch stock market data using Yahoo Finance API. This is an alternative source for stock data.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        function: Type of data to fetch. Options:
            - 'info': Get comprehensive stock information
            - 'history': Get historical price data (last 30 days)
            - 'history_1y': Get 1 year historical data
            - 'financials': Get financial statements
            - 'balance_sheet': Get balance sheet
            - 'cashflow': Get cash flow statement
            - 'recommendations': Get analyst recommendations
            - 'earnings': Get earnings data
            - 'dividends': Get dividend history
            - 'splits': Get stock split history
    
    Returns:
        JSON string with the requested data or error message
    """
    try:
        ticker = yf.Ticker(symbol)
        
        if function == "info":
            data = ticker.info
        elif function == "history":
            data = ticker.history(period="1mo").to_dict()
        elif function == "history_1y":
            data = ticker.history(period="1y").to_dict()
        elif function == "financials":
            data = ticker.financials.to_dict()
        elif function == "balance_sheet":
            data = ticker.balance_sheet.to_dict()
        elif function == "cashflow":
            data = ticker.cashflow.to_dict()
        elif function == "recommendations":
            recommendations = ticker.recommendations
            data = recommendations.to_dict() if recommendations is not None else {"message": "No recommendations available"}
        elif function == "earnings":
            data = {
                "quarterly": ticker.quarterly_earnings.to_dict() if ticker.quarterly_earnings is not None else {},
                "yearly": ticker.earnings.to_dict() if ticker.earnings is not None else {}
            }
        elif function == "dividends":
            dividends = ticker.dividends
            data = dividends.to_dict() if not dividends.empty else {"message": "No dividend history"}
        elif function == "splits":
            splits = ticker.splits
            data = splits.to_dict() if not splits.empty else {"message": "No stock splits"}
        else:
            return json.dumps({
                "error": f"Unknown function: {function}",
                "available_functions": ["info", "history", "history_1y", "financials", "balance_sheet", 
                                       "cashflow", "recommendations", "earnings", "dividends", "splits"]
            }, indent=2)
        
        return json.dumps({
            "success": True,
            "source": "Yahoo Finance",
            "function": function,
            "symbol": symbol,
            "data": data
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "success": False,
            "source": "Yahoo Finance",
            "error": f"Error fetching {function} data for {symbol}: {str(e)}",
            "message": "Yahoo Finance does not have this data available"
        }, indent=2)


@tool
def get_yahoo_market_data(symbols: str = "^GSPC,^DJI,^IXIC") -> str:
    """
    Fetch market indices data using Yahoo Finance API.
    
    Args:
        symbols: Comma-separated ticker symbols. Defaults to major indices:
            - ^GSPC: S&P 500
            - ^DJI: Dow Jones Industrial Average
            - ^IXIC: NASDAQ Composite
            - ^VIX: Volatility Index
    
    Returns:
        JSON string with market data or error message
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        results = {}
        
        for symbol in symbol_list:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="5d")
            
            results[symbol] = {
                "name": info.get("shortName", symbol),
                "current_price": info.get("regularMarketPrice", "N/A"),
                "previous_close": info.get("previousClose", "N/A"),
                "change": info.get("regularMarketChange", "N/A"),
                "change_percent": info.get("regularMarketChangePercent", "N/A"),
                "volume": info.get("volume", "N/A"),
                "last_5_days": history["Close"].to_dict() if not history.empty else {}
            }
        
        return json.dumps({
            "success": True,
            "source": "Yahoo Finance",
            "data": results
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "success": False,
            "source": "Yahoo Finance",
            "error": f"Error fetching market data: {str(e)}",
            "message": "Yahoo Finance does not have this data available"
        }, indent=2)


@tool
def search_yahoo_ticker(query: str) -> str:
    """
    Search for stock ticker symbols using Yahoo Finance.
    
    Args:
        query: Company name or partial ticker to search
    
    Returns:
        JSON string with matching ticker symbols or error message
    """
    try:
        ticker = yf.Ticker(query)
        info = ticker.info
        
        result = {
            "symbol": info.get("symbol", query),
            "name": info.get("longName", "N/A"),
            "exchange": info.get("exchange", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A")
        }
        
        return json.dumps({
            "success": True,
            "source": "Yahoo Finance",
            "data": result
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "success": False,
            "source": "Yahoo Finance",
            "error": f"Error searching for ticker '{query}': {str(e)}",
            "message": "Could not find ticker symbol"
        }, indent=2)