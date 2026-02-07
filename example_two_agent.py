"""
Example script demonstrating the Two-Agent System
"""
import yaml
from agent import create_two_agent_system, get_llm

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def main():
    print("="*70)
    print("Two-Agent System Example")
    print("="*70)
    
    # Initialize two-agent system
    provider = config.get('LLM_Model_provider', 'gemini').lower()
    print(f"\n🤖 Initializing Two-Agent System with {provider}...")
    
    try:
        orchestrator = create_two_agent_system(provider=provider)
        print("✅ System ready!\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Example queries
    examples = [
        "What is the current gold price?",
        "Show me Apple stock performance",
        "What's the silver price trend?",
    ]
    
    print("Running example queries:\n")
    
    for i, query in enumerate(examples, 1):
        print(f"\n{'='*70}")
        print(f"Example {i}: {query}")
        print('='*70)
        
        try:
            response = orchestrator.process_query(query, verbose=True)
            print(f"\n{'='*70}")
            print("FINAL RESPONSE:")
            print('='*70)
            print(response)
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        print("\n" + "="*70 + "\n")
        
        # Only run first example in demo mode
        user_continue = input("Continue to next example? (y/n): ").strip().lower()
        if user_continue != 'y':
            break
    
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    main()
