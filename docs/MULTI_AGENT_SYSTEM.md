# Two-Agent System Architecture

## Overview

The Trading Assistant now supports a **two-agent system** that separates concerns between data retrieval and analysis for better performance and clearer responsibilities.

## Architecture

### 🔄 Single Agent Mode (Original)
```
User Query → Single Agent → Tools + Analysis → Response
```

### 🤖🤖 Two-Agent System (New)
```
User Query → Orchestrator
              ↓
         Data Agent (retrieves data via tools)
              ↓
         Analysis Agent (analyzes data)
              ↓
         Combined Response
```

## Agents

### 1. Data Agent (`agents/data_agent.py`)
**Purpose**: Fetch market data from APIs

**Tools Available**:
- `get_stock_data` - OpenBB equity data
- `get_economic_data` - Economic indicators
- `get_market_overview` - Market overview
- `get_yahoo_stock_data` - Yahoo Finance data
- `get_yahoo_market_data` - Market indices
- `search_yahoo_ticker` - Ticker search

**Responsibilities**:
- ✅ Retrieve requested data using tools
- ✅ Handle commodity symbol mapping (Gold→XAU, Silver→XAG, etc.)
- ✅ Return structured raw data
- ❌ NO analysis or insights

### 2. Analysis Agent (`agents/analysis_agent.py`)
**Purpose**: Analyze financial data and provide insights

**Capabilities**:
- Technical analysis (trends, patterns, momentum)
- Fundamental analysis (ratios, financial health)
- Market sentiment interpretation
- Comparative analysis
- Risk assessment

**Responsibilities**:
- ✅ Analyze provided data
- ✅ Generate insights and interpretations
- ✅ Provide context and implications
- ❌ NO data fetching (no tools)

### 3. Orchestrator (`agents/orchestrator.py`)
**Purpose**: Coordinate workflow between agents

**Process**:
1. Receive user query
2. Route query to determine data needs
3. Data agent fetches data
4. Pass data to analysis agent
5. Combine and return results

## Usage

### CLI Mode

```bash
python agent_system.py
```

Choose mode when prompted:
- `1` - Single Agent (default)
- `2` - Two-Agent System

### Dashboard Mode

```bash
streamlit run dashboard.py
```

Select agent mode in sidebar:
- **Single Agent** - All-in-one agent
- **Two-Agent System** - Separate data + analysis

## Benefits of Two-Agent System

### ✅ Advantages
- **Separation of Concerns**: Clear division between data fetching and analysis
- **Better Prompts**: Each agent has specialized instructions
- **Improved Accuracy**: Data agent focuses on correct API calls, analysis agent focuses on insights
- **Debugging**: Easier to identify if issue is in data retrieval or analysis
- **Extensibility**: Can easily swap or upgrade individual agents

### 📊 When to Use

**Use Two-Agent System when**:
- Complex queries requiring deep analysis
- Want transparency in data vs. analysis
- Need to debug data retrieval issues
- Require detailed analytical insights

**Use Single Agent when**:
- Quick simple queries
- Speed is priority
- Simple data lookups
- Prefer streamlined approach

## Example Workflows

### Query: "What is the gold price trend?"

#### Two-Agent System:
```
1. Orchestrator routes query
2. Data Agent: Fetches XAU=F data via get_yahoo_stock_data
3. Analysis Agent: Analyzes price trends, identifies patterns
4. Returns: Detailed analysis + raw data
```

#### Single Agent:
```
1. Agent fetches XAU=F data and analyzes in one step
2. Returns: Combined response
```

## Commodity Mapping

Both systems support automatic commodity symbol mapping:

| Commodity | Symbols |
|-----------|---------|
| Gold | XAU=F, GC=F, GLD |
| Silver | XAG=F, SI=F, SLV |
| Oil | CL=F, BZ=F, USO |
| Copper | HG=F, COPX |
| Natural Gas | NG=F, UNG |

Query "gold price" or "XAU" → automatically routes to XAU=F

## Configuration

Edit `config.yaml` to set default LLM provider:

```yaml
LLM_Model_provider: "gemini"  # or openai, claude, etc.
```

Both agent modes use the same LLM provider.

## File Structure

```
Trading-Assistant/
├── agent_system.py            # Main entry point
├── dashboard.py               # Streamlit UI
├── agents/
│   ├── __init__.py            # Module init
│   ├── data_agent.py          # Data retrieval agent
│   ├── analysis_agent.py      # Analysis agent
│   └── orchestrator.py        # Agent coordinator
├── tools/
│   ├── openbb_tool.py         # OpenBB tools
│   └── yahoo_finance_tool.py  # Yahoo Finance tools
└── utils/
    └── query_router.py        # Query routing & commodity mapping
```

## Development

### Adding New Tools

Add tools to `data_agent.py` only:

```python
tools = [
    # existing tools...
    your_new_tool
]
```

### Modifying Analysis Logic

Edit prompts in `analysis_agent.py`:

```python
def load_analysis_agent_prompt() -> str:
    return """Your custom analysis instructions..."""
```

### Customizing Orchestration

Modify `orchestrator.py` to change workflow, add caching, or implement fallbacks.

## Troubleshooting

**Issue**: Data agent returns errors
- Check API keys in `.env`
- Verify tool parameters
- Check commodity symbol mapping

**Issue**: Analysis is generic
- Ensure data agent successfully retrieved data
- Check analysis agent prompt
- Verify data is being passed correctly

**Issue**: Slow performance
- Use Single Agent mode for simple queries
- Consider caching in orchestrator
- Check API rate limits

## Future Enhancements

- [ ] Add caching layer in orchestrator
- [ ] Support for more specialized agents (e.g., risk agent, news agent)
- [ ] Agent memory/conversation history
- [ ] Parallel tool execution in data agent
- [ ] Confidence scoring for analysis
- [ ] A/B testing between single and two-agent modes
