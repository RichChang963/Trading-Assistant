# Trading Assistant with LangChain & OpenBB & Yahoo Finance

An intelligent trading assistant powered by LangChain that integrates with OpenBB and Yahoo Finance for real-time market data. Supports multiple LLM providers: OpenAI, Google Gemini, Anthropic Claude, Perplexity, OpenRouter, and Ollama.

## Features

- 🤖 **Multi-LLM Support**: Choose between OpenAI, Google Gemini, Anthropic Claude, Perplexity, OpenRouter, or Ollama
- � **Two-Agent System**: Separate data retrieval from analysis for better performance and clarity
- 📊 **Real-time Market Data**: Access stock quotes, historical data, news, and company profiles via OpenBB and Yahoo Finance
- 📈 **Economic Indicators**: Fetch GDP, CPI, and other economic data
- 💬 **Conversational Interface**: Natural language queries for financial data
- 🌟 **Commodity Mapping**: Automatic symbol resolution (Gold→XAU, Silver→XAG, etc.)

## Installation

### 1. Clone the Repository

In order to install the application, first make sure you have _git_, _conda_ installed.

Then, clone the source code from GitHub onto your local machine and navigate into the `Trading-Assistant` directory. Finally, use the provided `environment.yaml` file to create the _conda_ environment.

```bash
git clone https://github.com/samarthiith/Trading-Assistant
cd Trading-Assistant
```

### 2. Create Conda Environment

```bash
conda env create -f envs/environment.yaml
conda activate trading
```

### 3. Set Up Environment Variables

Copy the example environment file and add your API keys:

```bash
cp credentials/.env.example credentials/.env
```

Edit `.env` and add your API keys:

- **OpenAI**: https://platform.openai.com/api-keys
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Anthropic Claude**: https://platform.claude.com/docs/en/api/admin/api_keys/retrieve
- **Perplexity**: https://www.perplexity.ai/settings/api
- **OpenRouter**: https://openrouter.ai/keys
- **OpenBB**: https://docs.openbb.co/python/extensions/interface/openbb-api

**Note**: Ollama runs locally and doesn't require an API key.

### 4. Set Up Model Config

Select the LLM model that you would like to us in the `config.yaml`.

## Usage

### 1. Basic Command-line (CLI) Usage

Run the agent:

```bash
python agent_system.py
```

You'll be prompted to choose between:
- **Single Agent Mode** (1): All-in-one agent handles everything
- **Two-Agent System** (2): Separate data retrieval and analysis

Example interaction with Two-Agent System:

```bash
Select mode:
1. Single Agent (default - all-in-one)
2. Two-Agent System (data retrieval + analysis)

Enter choice (1 or 2, default=1): 2

🤖 Initializing Two-Agent System with gemini...
✅ Two-Agent System ready!
   📡 Data Agent: Fetches market data
   📊 Analysis Agent: Provides insights

You: What's the gold price trend?
[Agent processes with two-phase approach: data → analysis]

You: Get me the latest news about Tesla
[Agent retrieves TSLA news then analyzes sentiment]
```

### 2. Running the Streamlit Dashboard

To run the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`. The app will enable you to interact in the chatbox.

In the sidebar, you can switch between:
- **Single Agent**: Traditional all-in-one approach
- **Two-Agent System**: Separate data fetching and analysis

## Agent Modes

### Single Agent Mode
Traditional approach where one agent handles both data retrieval and analysis.

```
User Query → Agent → Tools + Analysis → Response
```

### Two-Agent System
Modern architecture separating concerns:

```
User Query → Orchestrator
              ↓
         Data Agent (fetches data)
              ↓
         Analysis Agent (analyzes)
              ↓  
         Combined Response
```

**Benefits**:
- Clear separation between data and analysis
- Specialized prompts for each task
- Better debugging and transparency
- More accurate commodity symbol mapping

See [TWO_AGENT_SYSTEM.md](docs/TWO_AGENT_SYSTEM.md) for detailed documentation.

## Architecture

The agent uses LangChain's modern architecture (post v1.0.0).

## License

MIT License
