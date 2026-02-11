"""
Analysis Agent - Specialized in analyzing financial data and providing insights
"""
import pathlib
from langchain.agents import create_agent

from utils.settings import load_system_prompt_text

ROOT_FOLDER = pathlib.Path(__file__).parent.parent


def create_analysis_agent(llm):
    """
    Create an analysis agent specialized in interpreting market data.
    
    Parameters
    ----------
    llm : object
        Language model instance
        
    Returns
    -------
    AgentExecutor
        Agent specialized in data analysis (with no tools)
    """
    system_prompt_text = load_system_prompt_text("multi_agents.analyst_role.prompt.md")

    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=system_prompt_text,
    )

    return agent
