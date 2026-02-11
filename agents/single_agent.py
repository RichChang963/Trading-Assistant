"""
All-in-One Agent - Handles both data retrieval and analysis in a single agent, using all available tools.
"""
import pathlib
from langchain.agents import create_agent

from tools.openbb_tool import get_stock_data, get_economic_data, get_market_overview
from tools.yahoo_finance_tool import get_yahoo_stock_data, get_yahoo_market_data, search_yahoo_ticker
from utils.settings import load_system_prompt_text

ROOT_FOLDER = pathlib.Path(__file__).parent.parent


def create_all_in_one_agent(llm):
    """
    Create an all-in-one agent that can handle both data retrieval and analysis, using all available tools.
    
    Parameters
    ----------
    llm : object
        Language model instance
        
    Returns
    -------
    AgentExecutor
        Agent specialized in data retrieval
    """
    tools = [
        # OpenBB tools
        get_stock_data, 
        get_economic_data, 
        get_market_overview,
        # Yahoo Finance tools
        get_yahoo_stock_data,
        get_yahoo_market_data,
        search_yahoo_ticker
    ]
    system_prompt_text = load_system_prompt_text("single_agent.role.prompt.md")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt_text,
    )

    return agent
