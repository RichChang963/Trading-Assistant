import os
import pathlib
import uuid
import yaml
from dotenv import load_dotenv

from agents.analysis_agent import create_analysis_agent
from agents.orchestrator import LangGraphOrchestrator

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
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=api_mode, 
            api_key=api_key,
            temperature=0
        )
    elif provider == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=api_mode,
            api_key=api_key,
            temperature=0,
            # Anthropic respects tool usage better
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=api_mode,
            api_key=api_key,
            temperature=0
        )
    elif provider == "perplexity":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=api_mode,
            api_key=api_key,
            base_url="https://api.perplexity.ai",
            temperature=0
        )
    elif provider == "openrouter":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=api_mode,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0
        )
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        base_url = MODEL_CONFIG.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(
            model=api_mode,
            base_url=base_url,
            temperature=0
        )
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai', 'gemini', 'claude', 'perplexity', 'openrouter', or 'ollama'")


def create_two_agent_system(provider:str=None):
    """
    Create a two-agent system: one for data retrieval, one for analysis.
    
    Args:
        provider: LLM provider (openai, claude, gemini, etc.)
        
    Returns:
        TwoAgentOrchestrator instance that coordinates both agents
    """
    llm = get_llm(provider)

    analysis_agent = create_analysis_agent(llm)
    
    # Return orchestrator that manages both
    return LangGraphOrchestrator(analysis_agent)


def run_cli():
    """CLI function to run the trading assistant."""
    print("=== Welcome to the Trading Assistant CLI ===\n")
    
    try:
        provider = MODEL_CONFIG.get("LLM_Model_provider").lower()
        
        print(f"\n🤖 Initializing Agent System with {provider}...")
        orchestrator = create_two_agent_system(provider)
        print(f"✅ Agent System ready!")
        print("   📡 Data Agent: Fetches market data")
        print("   📊 Analysis Agent: Provides insights")
        
        print("\nType 'exit', 'quit', or 'q' to end the session.\n")

        session_id = f"cli-{uuid.uuid4().hex}"

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("See you next time!👋")
                break
            
            if not user_input:
                continue
            
            try:
                response = orchestrator.process_query(
                    user_input,
                    verbose=True,
                    session_id=session_id,
                )
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
