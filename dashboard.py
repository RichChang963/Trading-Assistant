import streamlit as st
import yaml
from utils.query_router import pass_and_return_rewritten_query
from agent import create_trading_agent

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

st.set_page_config(
    page_title="Trading Assistant",
    page_icon="📈",
    layout="wide"
)

# Header
st.title("📈 Trading Assistant")
st.caption("Powered by OpenBB & Yahoo Finance APIs")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("LLM Provider")
    provider = st.selectbox(
        "Select Model Provider",
        options=["gemini", "openai", "claude", "perplexity", "ollama"],
        index=(
            ["gemini", "openai", "claude", "perplexity", "ollama"].index(
                config.get('LLM_Model_provider', 'gemini')
            )
        ),
        help="Choose which AI model to use"
    )
    
    model_map = {
        "gemini": config.get('GEMINI_MODEL', 'gemini-2.5-flash'),
        "openai": config.get('OPENAI_MODEL', 'gpt-4o-mini'),
        "claude": config.get('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
        "perplexity": config.get('PERPLEXITY_MODEL', 'sonar-pro'),
        "ollama": config.get('OLLAMA_MODEL', 'llama3.2')
    }
    
    st.info(f"**Model:** {model_map[provider]}")
    
    # Clear chat history button
    st.subheader("Chat Controls")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        if 'agent' in st.session_state:
            del st.session_state.agent
        st.rerun()
    
    st.divider()

    st.caption("🔒 **Data Source: OpenBB & Yahoo Finance**")
    st.markdown("### 📈 OpenBB Tools")
    st.markdown("""
    - 📈 `get_stock_data`: quotes, historical, news, profile, financials
    - 📊 `get_economic_data`: GDP, CPI, unemployment, interest rates
    - 🌐 `get_market_overview`: indices, gainers, losers, sectors
    """)

    
    st.markdown("### 📈 Yahoo Finance Tools")
    st.markdown("""
    - 📈 `get_yahoo_stock_data`: info, history, financials, recommendations
    - 📊` get_yahoo_market_data`: market indices
    - 🌐 search_yahoo_ticker`: search ticker symbols
    """)

    st.divider()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Reinitialize agent if provider changes
if "current_provider" not in st.session_state or st.session_state.current_provider != provider:
    st.session_state.current_provider = provider
    with st.spinner(f"Initializing {provider} model..."):
        st.session_state.agent = create_trading_agent(provider=provider)
    st.success(f"✅ {provider.capitalize()} model loaded!")

# Initialize agent if not exists
if "agent" not in st.session_state:
    try:
        with st.spinner("Initializing agent..."):
            st.session_state.agent = create_trading_agent(provider=provider)
    except Exception as e:
        st.error(f"Error initializing agent: {str(e)}")
        st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask me about stocks, markets, or economic data...")

if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    # Get AI response with enhanced query
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = pass_and_return_rewritten_query(user_input, st.session_state.agent)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
