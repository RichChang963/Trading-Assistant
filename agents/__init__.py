"""
Multi-agent system for trading assistance.
Separates data retrieval from analysis.
"""

from .data_agent import create_data_agent
from .analysis_agent import create_analysis_agent
from .orchestrator import TwoAgentOrchestrator

__all__ = ['create_data_agent', 'create_analysis_agent', 'TwoAgentOrchestrator']
