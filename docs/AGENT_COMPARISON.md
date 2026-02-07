# Agent System Comparison

## Quick Reference Guide

### When to Use Each Mode

| Scenario | Single Agent | Two-Agent System |
|----------|--------------|------------------|
| Quick price lookup | ✅ Recommended | ⚪ Works but slower |
| Deep analysis needed | ⚪ Basic | ✅ Recommended |
| Debugging data issues | ❌ Hard to isolate | ✅ Easy to debug |
| Speed priority | ✅ Faster | ⚪ Slightly slower |
| Need data transparency | ⚪ Mixed output | ✅ Clear separation |
| Complex queries | ⚪ Can get confused | ✅ Better structured |
| Simple questions | ✅ Perfect | ⚪ Overkill |

## Architecture Diagrams

### Single Agent Mode
```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Single Agent      │
│  ┌───────────────┐  │
│  │ Data Tools    │  │
│  ├───────────────┤  │
│  │ Analysis      │  │
│  │ Logic         │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│  Response   │
└─────────────┘
```

### Two-Agent System
```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Orchestrator    │
└──────┬───────────┘
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌──────────────┐    ┌───────────────┐
│ Data Agent   │    │ Analysis      │
│              │───▶│ Agent         │
│ ┌──────────┐ │    │               │
│ │  Tools   │ │    │ ┌───────────┐ │
│ │  - OBB   │ │    │ │ Insights  │ │
│ │  - Yahoo │ │    │ │ Patterns  │ │
│ │  - Search│ │    │ │ Context   │ │
│ └──────────┘ │    │ └───────────┘ │
└──────────────┘    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Combined      │
                    │ Response      │
                    └───────────────┘
```

## Response Format Comparison

### Single Agent Response
```
Here's the information about gold:

The current price of gold (XAU) is $2,123.45 per ounce, 
up 1.2% from yesterday. This represents a bullish trend 
with strong support at $2,100...
```

### Two-Agent System Response
```
## 📊 Analysis Results

### Key Findings
- Current price: $2,123.45 (+1.2%)
- Support level: $2,100
- Resistance: $2,150

### Technical Analysis
The gold price shows bullish momentum with...

### Market Context
This increase aligns with...

---
📁 View Raw Data
[Expandable section with complete API response]
```

## Performance Comparison

| Metric | Single Agent | Two-Agent |
|--------|--------------|-----------|
| Response Time | ~3-5 sec | ~5-8 sec |
| Data Accuracy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Analysis Depth | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Debugging | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Code Clarity | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Resource Usage | Lower | Higher |

## Example Use Cases

### Best for Single Agent
- "What's AAPL stock price?"
- "Show me TSLA quote"
- "Get current market indices"
- Simple data lookups

### Best for Two-Agent System
- "Analyze gold price trends over the past year"
- "Compare Apple and Microsoft financial performance"
- "What does the recent CPI data mean for markets?"
- "Analyze silver volatility and provide risk assessment"

## Code Examples

### Using Single Agent
```python
from agent import create_trading_agent

agent = create_trading_agent(provider="gemini")
response = agent.invoke({"messages": [("user", "What's gold price?")]})
```

### Using Two-Agent System
```python
from agent import create_two_agent_system

orchestrator = create_two_agent_system(provider="gemini")
response = orchestrator.process_query("What's gold price?", verbose=True)
```

## Error Handling

### Single Agent
❌ Hard to tell if error is in:
- Data retrieval?
- Analysis logic?
- Tool selection?

### Two-Agent System
✅ Clear error location:
- **Phase 1 Error**: Data retrieval issue (API, ticker symbol, etc.)
- **Phase 2 Error**: Analysis issue (LLM, prompt, etc.)

## Migration Guide

### Switching from Single to Two-Agent

**CLI:**
Just select option `2` when prompted

**Dashboard:**
Select "Two-Agent System" in sidebar radio button

**Programmatic:**
```python
# Before
agent = create_trading_agent("gemini")
response = pass_and_return_rewritten_query(query, agent)

# After
orchestrator = create_two_agent_system("gemini")
response = orchestrator.process_query(query, verbose=False)
```

## Advanced Configuration

### Custom Data Agent
```python
from agents.data_agent import create_data_agent

llm = get_llm("gemini")
custom_data_agent = create_data_agent(llm)
# Modify tools or prompts as needed
```

### Custom Analysis Agent
```python
from agents.analysis_agent import create_analysis_agent

llm = get_llm("gemini")
custom_analysis_agent = create_analysis_agent(llm)
# Customize analysis frameworks
```

### Custom Orchestrator
```python
from agents.orchestrator import TwoAgentOrchestrator

orchestrator = TwoAgentOrchestrator(
    data_agent=custom_data_agent,
    analysis_agent=custom_analysis_agent
)
```

## Troubleshooting

### Issue: Two-agent system is slow
**Solution:** Use single agent for simple queries, two-agent for complex analysis

### Issue: Data phase fails repeatedly
**Solution:** Check API keys, verify ticker symbols, review commodity mappings

### Issue: Analysis is generic
**Solution:** Ensure data agent returns sufficient data; customize analysis prompt

### Issue: Can't see raw data
**Solution:** Use verbose=True in CLI or expand "View Raw Data" in dashboard

## Future Enhancements

Potential improvements to the two-agent system:
- [ ] Caching layer to avoid redundant API calls
- [ ] Parallel data fetching for multiple symbols
- [ ] Agent memory for follow-up questions
- [ ] Confidence scoring
- [ ] Multiple analysis agents (technical, fundamental, sentiment)
- [ ] Agent voting/consensus mechanism
