from langchain.tools import tool
from openbb import obb
import json


@tool
def get_stock_data(symbol: str, function: str = "quote") -> str:
    """
    Fetch stock market data using OpenBB.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        function: Type of data to fetch. Options:
            - 'quote': Get current stock quote
            - 'historical': Get historical price data
            - 'news': Get latest news
            - 'profile': Get company profile
    
    Returns:
        JSON string with the requested data
    """
    try:
        if function == "quote":
            data = obb.equity.price.quote(symbol)
        elif function == "historical":
            data = obb.equity.price.historical(symbol, provider="yfinance")
        elif function == "news":
            data = obb.news.company(symbol)
        elif function == "profile":
            data = obb.equity.profile(symbol)
        else:
            return f"Unknown function: {function}. Available: quote, historical, news, profile"
        
        # Convert to dict if it's an OBBject
        if hasattr(data, 'to_dict'):
            result = data.to_dict()
        else:
            result = str(data)
        
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error fetching data for {symbol}: {str(e)}"


@tool
def get_economic_data(indicator: str, country: str = "US") -> str:
    """
    Fetch economic indicators using OpenBB.
    
    Args:
        indicator: Economic indicator (e.g., 'gdp', 'cpi', 'unemployment')
        country: Country code (default: 'US')
    
    Returns:
        JSON string with economic data
    """
    try:
        if indicator.lower() == "gdp":
            data = obb.economy.gdp(country=country)
        elif indicator.lower() == "cpi":
            data = obb.economy.cpi(country=country)
        else:
            return f"Indicator '{indicator}' not yet supported. Try: gdp, cpi"
        
        if hasattr(data, 'to_dict'):
            result = data.to_dict()
        else:
            result = str(data)
        
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error fetching {indicator} data: {str(e)}"
