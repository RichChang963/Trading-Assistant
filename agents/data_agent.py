"""
Data Retrieval Agent - Specialized in fetching market data from APIs
"""
import pathlib
from langchain.agents import create_agent
from tools.openbb_tool import get_stock_data, get_economic_data, get_market_overview
from tools.yahoo_finance_tool import get_yahoo_stock_data, get_yahoo_market_data, search_yahoo_ticker
from utils.settings import load_system_prompt

ROOT_FOLDER = pathlib.Path(__file__).parent.parent


def create_data_agent(llm):
    """
    Create a data retrieval agent specialized in fetching market data.
    
    Args:
        llm: Language model instance
        
    Returns:
        Agent specialized in data retrieval
    """
    tools = [
        get_stock_data,
        get_economic_data,
        get_market_overview,
        get_yahoo_stock_data,
        get_yahoo_market_data,
        search_yahoo_ticker
    ]
    
    system_prompt = load_system_prompt("multi_agents.data_eng_role.prompt.md")
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )
    
    return agent
