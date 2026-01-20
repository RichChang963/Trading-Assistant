# Trading Assistant with LangChain & OpenBB

An intelligent trading assistant powered by LangChain that integrates with OpenBB for real-time market data. Supports multiple LLM providers: OpenAI, Google Gemini, and Perplexity.

## Features

- 🤖 **Multi-LLM Support**: Choose between OpenAI, Google Gemini, or Perplexity
- 📊 **Real-time Market Data**: Access stock quotes, historical data, news, and company profiles via OpenBB
- 📈 **Economic Indicators**: Fetch GDP, CPI, and other economic data
- 💬 **Conversational Interface**: Natural language queries for financial data

## Installation

### 1. Clone the Repository

```bash
cd /home/ycc/Trading-Assistant
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
- **Perplexity**: https://www.perplexity.ai/settings/api
- **OpenBB**: https://docs.openbb.co/python/extensions/interface/openbb-api

### 4. Set Up Model Config

Select the LLM model that you would like to us in the `config.yaml`.

## Usage

### 1. Basic Command-line (CLI) Usage

Run the agent:

```bash
python agent.py
```

You will see the initalization and then you can start to ask questions (taking Openai as an example):

```bash
Agent initialized with openai ✅
Type 'exit' or 'quit' to end the session.

You: What's the current price of Apple stock?
Assistant: [Agent fetches and analyzes AAPL data]

You: Get me the latest news about Tesla
Assistant: [Agent retrieves TSLA news]
```

### 2. Running the Streamlit Dashboard

To run the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`. The app will enable you to interact in the chatbox.

## Architecture

The agent uses LangChain's modern architecture (post v1.0.0).

## License

MIT License
