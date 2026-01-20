import streamlit as st
from agent import create_trading_agent, MODEL_CONFIG

st.set_page_config(
    page_title="Trading Assistant",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    try:
        provider = MODEL_CONFIG.get("LLM_Model_provider", "openai").lower()
        st.session_state.agent = create_trading_agent(provider)
        st.session_state.provider = provider
    except Exception as e:
        st.error(f"Error initializing agent: {str(e)}")
        st.stop()

# Header
st.title("📈 Trading Assistant")
st.caption(f"Powered by {st.session_state.provider.upper()} & OpenBB")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about stocks, economic data, or market analysis..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = st.session_state.agent.invoke({"messages": [("user", prompt)]})
                assistant_message = response['messages'][-1].content
                st.markdown(assistant_message)
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar
with st.sidebar:
    st.header("Options")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("Agent capabilities:")
    st.markdown("""
    - 📊 Stock quotes & historical data
    - 📰 Market news
    - 🏢 Company profiles
    - 📈 Economic indicators (GDP, CPI)
    - 💡 Financial analysis
    """)
