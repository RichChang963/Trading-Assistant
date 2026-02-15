import uuid
import re
from pathlib import Path
import streamlit as st
from streamlit_markdown import st_markdown
import yaml

from agent_system import create_two_agent_system
from utils.settings import json_to_dataframe

LLM_LIST = ["gemini", "openai", "claude", "perplexity", "openrouter", "ollama"]


def _extract_raw_json(response_text: str) -> tuple[str, str | None]:
    """Split assistant response into analysis text and raw JSON block."""
    details_pattern = re.compile(
        r"<details>.*?<summary>.*?</summary>\s*(.*?)\s*</details>",
        re.DOTALL | re.IGNORECASE,
    )
    match = details_pattern.search(response_text)
    if not match:
        return response_text.strip(), None

    raw_json = match.group(1).strip()
    analysis_text = details_pattern.sub("", response_text).strip()
    return analysis_text, raw_json


# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

st.set_page_config(
    page_title="Trading Assistant",
    page_icon="📈",
    layout="wide"
)

tab1, tab2 = st.tabs(["🏠 Trading Assistant", "📚 Documentation"])

with tab1:
    # Header
    st.title("Trading Assistant Chatbox")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.subheader("🤖 Agent Mode")
        agent_mode = st.radio(
            "Select Agent System",
            options=["Two-Agent System"],
            index=0,
            help="Two-Agent: Separate data retrieval & analysis"
        )
        
        if agent_mode == "Two-Agent System":
            st.info(
                "📡 **Data Agent** fetches data\n\n📊 "
                "**Analysis Agent** provides insights"
            )
        else:
            st.info("🤖 **All-in-one agent** handles everything")

        provider = st.selectbox(
            "Select Model Provider",
            options=LLM_LIST,
            index=(LLM_LIST.index(config.get("LLM_Model_provider", "gemini"))
            ),
            help="Choose which AI model to use"
        )
        
        model_map = {
            "gemini": config.get("GEMINI_MODEL", "gemini-2.5-flash"),
            "openai": config.get("OPENAI_MODEL", "gpt-4o-mini"),
            "claude": config.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
            "perplexity": config.get("PERPLEXITY_MODEL", "sonar-pro"),
            "openrouter": config.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            "ollama": config.get("OLLAMA_MODEL", "llama3.2")
        }
        
        st.info(f"**Model:** {model_map[provider]}")
        
        # Clear chat history button
        st.subheader("Chat Controls")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            if "agent" in st.session_state:
                del st.session_state.agent
            if "orchestrator" in st.session_state:
                del st.session_state.orchestrator
            st.rerun()
        
        st.divider()

        st.subheader("Data Sourcs")
        st.markdown("OpenBB (using Yahoo Finance & OECD as two main sources)")
        
        st.subheader("Example questions - Two-Agent System")
        st.markdown("- Tell me about Apple stock")
        st.markdown("- What is the gold price trend?")
        st.markdown("- Analyze gold price trends over the past year")
        st.markdown("- Compare Apple and Microsoft financial performance")
        st.markdown("- What does recent interest rate in Germany look like?")

        st.divider()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"ui-{uuid.uuid4().hex}"

    # Reinitialize if provider or mode changes
    reinit_needed = False
    if ("current_provider" not in st.session_state) or (
        st.session_state.current_provider != provider
    ):
        st.session_state.current_provider = provider
        reinit_needed = True

    if ("current_mode" not in st.session_state) or (
        st.session_state.current_mode != agent_mode
    ):
        st.session_state.current_mode = agent_mode
        reinit_needed = True

    if reinit_needed:
        with st.spinner(f"Initializing {agent_mode} with {provider}..."):
            if agent_mode == "Two-Agent System":
                st.session_state.orchestrator = create_two_agent_system(
                    provider=provider
                )
                if "agent" in st.session_state:
                    del st.session_state.agent

        st.success(f"✅ {agent_mode} with {provider.capitalize()} loaded!")

    # Initialize on first load
    if agent_mode == "Two-Agent System" and "orchestrator" not in st.session_state:
        try:
            with st.spinner("Initializing Two-Agent System..."):
                st.session_state.orchestrator = create_two_agent_system(
                    provider=provider
                )
        except Exception as e:
            st.error(f"Error initializing orchestrator: {str(e)}")
            st.stop()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            df = message.get("dataframe")
            if df is not None:
                st.dataframe(df, use_container_width=True)

    # Chat input
    user_input = st.chat_input("Ask me about stocks, markets, or economic data...")

    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
    
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    if agent_mode == "Two-Agent System":
                        response = st.session_state.orchestrator.process_query(
                            user_input,
                            verbose=False,
                            session_id=st.session_state.session_id,
                        )
                    analysis_text, raw_json = _extract_raw_json(response)

                    df = json_to_dataframe(raw_json, debug=True) if raw_json else None
                    st.markdown(analysis_text)
                    if df is not None:
                        st.dataframe(df, use_container_width=True)
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": analysis_text,
                            # "dataframe": df,
                        }
                    )
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
        # Rerun to display new messages
        st.rerun()
with tab2:
    st.header("Documentation")
    docs_path = Path("docs")
    md_files = list(docs_path.glob("*.md"))
    
    doc_names = [f.stem.replace("_", " ").title() for f in md_files]
    selected = st.selectbox("Select Document", doc_names)
    
    selected_file = md_files[doc_names.index(selected)]
    md = Path(selected_file).read_text(encoding="utf-8")
    st_markdown(content=md, theme_color="light", mermaid_theme="default")
