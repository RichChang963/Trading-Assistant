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
    "ollama": None,  # Ollama runs locally, no API key needed
}


def load_system_prompt() -> str:
    """Load system prompt from markdown file."""
    prompt_path = ROOT_FOLDER / ".github" / "prompts" / "role.prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
    

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
    elif provider == "ollama":
        base_url = MODEL_CONFIG.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(
            model=api_mode,
            base_url=base_url,
            temperature=0
        )
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai', 'gemini', 'claude', 'perplexity', or 'ollama'")


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
    
    system_message = load_system_prompt()
    
    # Add extra enforcement in system prompt
    strict_enforcement = """
    🚨 ABSOLUTE REQUIREMENT 🚨
    You are FORBIDDEN from using web search or external knowledge.
    You MUST ONLY use the provided tools: get_stock_data, get_economic_data, get_market_overview, get_yahoo_stock_data, get_yahoo_market_data, search_yahoo_ticker.

    BEFORE answering ANY question:
    1. Identify which tool to use
    2. Call the tool with appropriate parameters
    3. Use ONLY the tool's output in your response
    4. If no tool can answer, say: "I cannot answer this without OpenBB or Yahoo Finance data."

    DO NOT access web search. DO NOT use pre-trained knowledge. ONLY USE TOOLS.

    Example for "gold price past 5 years":
    - Use: get_yahoo_stock_data('GC=F', 'history_1y') for gold futures
    - OR: get_stock_data('GLD', 'historical') for gold ETF
    """
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_message + strict_enforcement,
    )
    
    return agent


def run_cli():
    """CLI function to run the trading assistant."""
    print("=== Trading Assistant with LangChain & OpenBB & Yahoo Finance ===\n")
    
    try:
        provider = MODEL_CONFIG.get("LLM_Model_provider").lower()
        agent = create_trading_agent(provider)
        print(f"\nAgent initialized with {provider} ✅")
        print("Type 'exit', 'quit', or 'q' to end the session.\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("See you next time!👋")
                break
            
            if not user_input:
                continue
            
            try:
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
