import os
import pathlib
import yaml
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from utils.query_router import pass_and_return_rewritten_query
from tools.openbb_tool import get_stock_data, get_economic_data, get_market_overview
from tools.yahoo_finance_tool import get_yahoo_stock_data, get_yahoo_market_data, search_yahoo_ticker
from agents.data_agent import create_data_agent
from agents.analysis_agent import create_analysis_agent
from agents.orchestrator import TwoAgentOrchestrator
from utils.settings import load_system_prompt

ROOT_FOLDER = pathlib.Path(__file__).parent

# Load config.yaml
config_path = ROOT_FOLDER / "config.yaml"
with open(config_path, "r") as file:
    MODEL_CONFIG = yaml.safe_load(file)

load_dotenv()
env_path = ROOT_FOLDER / "credentials" / ".env"
load_dotenv(dotenv_path=env_path)

LLM_MODEL_API_DICT = {
    "openai": "OPENAI_API_KEY",
    "claude": "CLAUDE_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "ollama": None,  # Ollama runs locally, no API key needed
}
    

def get_llm(provider:str=None):
    """Get LLM with strict tool-only configuration."""
    model_api_key = LLM_MODEL_API_DICT.get(provider, "")
    api_key = os.getenv(model_api_key) if model_api_key else None
    api_mode = MODEL_CONFIG.get(f"{provider.upper()}_MODEL", "gpt-4o-mini")

    if model_api_key and not api_key:
        raise ValueError(f"{model_api_key} not found in environment")
    
    if provider == "openai":
        return ChatOpenAI(
            model=api_mode, 
            api_key=api_key,
            temperature=0
        )
    elif provider == "claude":
        return ChatAnthropic(
            model=api_mode,
            api_key=api_key,
            temperature=0,
            # Anthropic respects tool usage better
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=api_mode,
            api_key=api_key,
            temperature=0
        )
    elif provider == "perplexity":
        return ChatOpenAI(
            model=api_mode,
            api_key=api_key,
            base_url="https://api.perplexity.ai",
            temperature=0
        )
    elif provider == "openrouter":
        return ChatOpenAI(
            model=api_mode,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0
        )
    elif provider == "ollama":
        base_url = MODEL_CONFIG.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(
            model=api_mode,
            base_url=base_url,
            temperature=0
        )
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai', 'gemini', 'claude', 'perplexity', 'openrouter', or 'ollama'")


def create_trading_agent(provider:str=None):
    """Create a trading assistant agent with OpenBB and Yahoo Finance tools ONLY."""
    llm = get_llm(provider)
    
    # All available tools from both OpenBB and Yahoo Finance
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
    
    system_message = load_system_prompt("single_agent.role.prompt.md")
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_message,
    )
    
    return agent


def create_two_agent_system(provider:str=None):
    """
    Create a two-agent system: one for data retrieval, one for analysis.
    
    Args:
        provider: LLM provider (openai, claude, gemini, etc.)
        
    Returns:
        TwoAgentOrchestrator instance that coordinates both agents
    """
    llm = get_llm(provider)
    
    # Create specialized agents
    data_agent = create_data_agent(llm)
    analysis_agent = create_analysis_agent(llm)
    
    # Return orchestrator that manages both
    return TwoAgentOrchestrator(data_agent, analysis_agent)


def run_cli():
    """CLI function to run the trading assistant."""
    print("=== Trading Assistant with LangChain & OpenBB & Yahoo Finance ===\n")
    
    try:
        provider = MODEL_CONFIG.get("LLM_Model_provider").lower()
        
        # Ask user which mode they want
        print("Select mode:")
        print("1. Single Agent (default - all-in-one)")
        print("2. Two-Agent System (data retrieval + analysis)")
        mode_choice = input("\nEnter choice (1 or 2, default=1): ").strip() or "1"
        
        if mode_choice == "2":
            print(f"\n🤖 Initializing Two-Agent System with {provider}...")
            orchestrator = create_two_agent_system(provider)
            print(f"✅ Two-Agent System ready!")
            print("   📡 Data Agent: Fetches market data")
            print("   📊 Analysis Agent: Provides insights")
            use_two_agent = True
        else:
            print(f"\n🤖 Initializing Single Agent with {provider}...")
            agent = create_trading_agent(provider)
            print(f"✅ Single Agent ready!")
            use_two_agent = False
        
        print("\nType 'exit', 'quit', or 'q' to end the session.\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("See you next time!👋")
                break
            
            if not user_input:
                continue
            
            try:
                if use_two_agent:
                    response = orchestrator.process_query(user_input, verbose=True)
                else:
                    response = pass_and_return_rewritten_query(user_input, agent)
                print(f"\nAssistant: {response}\n")
            except Exception as e:
                print(f"\nError: {str(e)}\n")
    except Exception as e:
        print(f"Error initializing agent: {str(e)}")


def main():
    """Main function - defaults to CLI."""
    run_cli()


if __name__ == "__main__":
    main()
