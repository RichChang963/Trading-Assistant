import os
import pathlib
import yaml
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.openbb_tool import get_stock_data, get_economic_data

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
    "gemini": "GOOGLE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
}

def get_llm(provider:str=None):
    """Initialize and return the selected LLM."""
    model_api_key = LLM_MODEL_API_DICT.get(provider, "")
    api_key = os.getenv(model_api_key)
    api_mode = MODEL_CONFIG.get(f"{provider.upper()}_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError(f"{model_api_key} not found in environment")
    
    if provider == "openai":
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    elif provider == "perplexity":
        return ChatOpenAI(
            model=api_mode,
            api_key=api_key,
            base_url="https://api.perplexity.ai",
            temperature=0
        )
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai', 'gemini', or 'perplexity'")


def create_trading_agent(provider:str=None):
    """Create a trading assistant agent with OpenBB tools."""
    llm = get_llm(provider)
    
    tools = [get_stock_data, get_economic_data]
    
    system_message = (
    """You are a helpful financial analyst assistant with access to real-time market \n
    data through OpenBB.
        
    Your capabilities include:
    - Fetching stock quotes, historical data, news, and company profiles
    - Retrieving economic indicators like GDP and CPI
    - Analyzing financial data and providing insights

    Always provide clear, concise answers based on the data you retrieve. If you need \n
    to fetch data, use the available tools. The values shall be from OpenBB only if \n
    it is available. The other news or content-wise information can be from other \n 
    available sources or tools.
    
    The output shall remove string like [1][2][3] since those are just reference."""
    )
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_message,
    )
    
    return agent


def run_cli():
    """CLI function to run the trading assistant."""
    print("=== Trading Assistant with LangChain & OpenBB ===\n")
    
    try:
        provider = MODEL_CONFIG.get("LLM_Model_provider").lower()
        agent = create_trading_agent(provider)
        print(f"\nAgent initialized with {provider} ✅")
        print("Type 'exit' or 'quit' to end the session.\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit']:
                print("See you next time!")
                break
            
            if not user_input:
                continue
            
            try:
                response = agent.invoke({"messages": [("user", user_input)]})
                print(f"\nAssistant: {response['messages'][-1].content}\n")
            except Exception as e:
                print(f"\nError: {str(e)}\n")
    except Exception as e:
        print(f"Error initializing agent: {str(e)}")


def main():
    """Main function - defaults to CLI."""
    run_cli()


if __name__ == "__main__":
    main()
