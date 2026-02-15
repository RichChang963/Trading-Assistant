"""Data retrieval agent for fetching market data.

Provides a helper to create a data agent configured with the system prompt.
"""
import pathlib
from langchain.agents import create_agent

from tools.openbb_tool import get_stock_data, get_economic_data, get_market_overview
from utils.settings import load_system_prompt_text

ROOT_FOLDER = pathlib.Path(__file__).parent.parent


def create_data_agent(llm):
    """
    Create a data retrieval agent specialized in fetching market data.
    
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
    ]
    system_prompt_text = load_system_prompt_text("multi_agents.data_eng_role.prompt.md")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt_text,
    )

    return agent
