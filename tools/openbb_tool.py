from langchain.tools import tool
from openbb import obb
import json


@tool
def get_stock_data(symbol: str, function: str = "quote") -> str:
    """
    Fetch stock market data using OpenBB. This is the ONLY source for stock data.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        function: Type of data to fetch. Options:
            - 'quote': Get current stock quote (price, volume, market cap)
            - 'historical': Get historical price data (OHLCV)
            - 'news': Get latest company news
            - 'profile': Get company profile and fundamentals
            - 'income': Get income statement
            - 'balance': Get balance sheet
            - 'cash': Get cash flow statement
            - 'metrics': Get key financial metrics
    
    Returns:
        JSON string with the requested data or error message
    """
    try:
        if function == "quote":
            data = obb.equity.price.quote(symbol, provider="yfinance")
        elif function == "historical":
            data = obb.equity.price.historical(symbol, provider="yfinance")
        elif function == "news":
            data = obb.news.company(symbol, provider="benzinga")
        elif function == "profile":
            data = obb.equity.profile(symbol, provider="fmp")
        elif function == "income":
            data = obb.equity.fundamental.income(symbol, provider="fmp", period="annual", limit=5)
        elif function == "balance":
            data = obb.equity.fundamental.balance(symbol, provider="fmp", period="annual", limit=5)
        elif function == "cash":
            data = obb.equity.fundamental.cash(symbol, provider="fmp", period="annual", limit=5)
        elif function == "metrics":
            data = obb.equity.fundamental.metrics(symbol, provider="fmp", period="annual", limit=5)
        else:
            return json.dumps({
                "error": f"Unknown function: {function}",
                "available_functions": ["quote", "historical", "news", "profile", "income", "balance", "cash", "metrics"]
            }, indent=2)
        
        # Convert to dict if it's an OBBject
        if hasattr(data, 'to_dict'):
            result = data.to_dict()
        elif hasattr(data, 'results'):
            result = [item.model_dump() if hasattr(item, 'model_dump') else str(item) for item in data.results]
        else:
            result = str(data)
        
        return json.dumps({"success": True, "function": function, "symbol": symbol, "data": result}, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error fetching {function} data for {symbol}: {str(e)}",
            "message": "OpenBB does not have this data available"
        }, indent=2)


@tool
def get_economic_data(indicator: str, country: str = "US") -> str:
    """
    Fetch economic indicators using OpenBB. This is the ONLY source for economic data.
    
    Args:
        indicator: Economic indicator. Options:
            - 'gdp': Gross Domestic Product
            - 'cpi': Consumer Price Index (inflation)
            - 'unemployment': Unemployment rate
            - 'interest_rate': Federal funds rate
            - 'retail_sales': Retail sales data
        country: Country code (default: 'US')
    
    Returns:
        JSON string with economic data or error message
    """
    try:
        indicator_lower = indicator.lower()
        
        if indicator_lower == "gdp":
            data = obb.economy.gdp(country=country, provider="oecd")
        elif indicator_lower == "cpi":
            data = obb.economy.cpi(country=country, provider="fred")
        elif indicator_lower in ["unemployment", "unemployment_rate"]:
            data = obb.economy.unemployment(country=country, provider="oecd")
        elif indicator_lower in ["interest_rate", "fed_funds"]:
            data = obb.economy.fred_series(series_id="FEDFUNDS", provider="fred")
        elif indicator_lower == "retail_sales":
            data = obb.economy.retail_sales(country=country, provider="fred")
        else:
            return json.dumps({
                "error": f"Unknown indicator: {indicator}",
                "available_indicators": ["gdp", "cpi", "unemployment", "interest_rate", "retail_sales"]
            }, indent=2)
        
        if hasattr(data, 'to_dict'):
            result = data.to_dict()
        elif hasattr(data, 'results'):
            result = [item.model_dump() if hasattr(item, 'model_dump') else str(item) for item in data.results]
        else:
            result = str(data)
        
        return json.dumps({"success": True, "indicator": indicator, "country": country, "data": result}, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error fetching {indicator} data for {country}: {str(e)}",
            "message": "OpenBB does not have this data available"
        }, indent=2)


@tool
def get_market_overview(data_type: str = "indices") -> str:
    """
    Fetch general market overview data using OpenBB. This is the ONLY source for market data.
    
    Args:
        data_type: Type of market data. Options:
            - 'indices': Major market indices (S&P 500, NASDAQ, DOW)
            - 'gainers': Top gaining stocks
            - 'losers': Top losing stocks
            - 'active': Most actively traded stocks
            - 'sectors': Sector performance
    
    Returns:
        JSON string with market data or error message
    """
    try:
        data_type_lower = data_type.lower()
        
        if data_type_lower == "indices":
            data = obb.index.market(provider="yfinance")
        elif data_type_lower == "gainers":
            data = obb.equity.discovery.gainers(provider="yfinance")
        elif data_type_lower == "losers":
            data = obb.equity.discovery.losers(provider="yfinance")
        elif data_type_lower == "active":
            data = obb.equity.discovery.active(provider="yfinance")
        elif data_type_lower == "sectors":
            data = obb.equity.sectors.performance(provider="yfinance")
        else:
            return json.dumps({
                "error": f"Unknown data type: {data_type}",
                "available_types": ["indices", "gainers", "losers", "active", "sectors"]
            }, indent=2)
        
        if hasattr(data, 'to_dict'):
            result = data.to_dict()
        elif hasattr(data, 'results'):
            result = [item.model_dump() if hasattr(item, 'model_dump') else str(item) for item in data.results]
        else:
            result = str(data)
        
        return json.dumps({"success": True, "data_type": data_type, "data": result}, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error fetching {data_type} market data: {str(e)}",
            "message": "OpenBB does not have this data available"
        }, indent=2)