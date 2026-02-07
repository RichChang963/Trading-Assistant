"""
Analysis Agent - Specialized in analyzing financial data and providing insights
"""
import pathlib
from langchain.agents import create_agent
from utils.settings import load_system_prompt

ROOT_FOLDER = pathlib.Path(__file__).parent.parent


def create_analysis_agent(llm):
    """
    Create an analysis agent specialized in financial analysis.
    
    Args:
        llm: Language model instance
        
    Returns:
        Agent specialized in data analysis (with no tools)
    """
    system_prompt = load_system_prompt("multi_agents.analyst_role.prompt.md")
    
    # Analysis agent has NO tools - it only analyzes provided data
    agent = create_agent(
        model=llm,
        tools=[],  # No tools for analysis agent
        system_prompt=system_prompt,
    )
    
    return agent
