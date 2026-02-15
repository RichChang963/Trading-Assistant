# Agent System Comparison

## Quick Reference Guide

### When to Use Each Mode

| Scenario | Two-Agent System |
|----------|------------------|
| Quick price lookup | ⚪ Works but slower |
| Deep analysis needed | ✅ Recommended |
| Debugging data issues | ✅ Easy to debug |
| Speed priority | ⚪ Slightly slower |
| Need data transparency | ✅ Clear separation |
| Complex queries | ✅ Better structured |
| Simple questions | ⚪ Overkill |

-----------------------------------------------------

## Architecture Diagrams

### Two-Agent System

```mermaid
graph LR
    A[User Query] --> B[Orchestrator]
    B --> C[Data Agent]
    B --> D[Analysis Agent]
    
    subgraph C[Data Agent]
        C1[Tools<br/>- OpenBB<br/>- Yahoo<br/>]
    end
    
    C --> D
    
    subgraph D[Analysis Agent]
        D1[Insights<br/>Patterns<br/>Context]
    end
    
    D --> E[Combined Response]
```

-----------------------------------------------------

## Response Format Comparison

### Two-Agent System Response

```md
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

-----------------------------------------------------

## Example Use Cases

### Best for Two-Agent System

- "Analyze gold price trends over the past year"
- "Compare Apple and Microsoft financial performance"
- "What does the recent CPI data in Gemrany mean for markets?"

-----------------------------------------------------

## Migration Guide

### Switching from Single to Two-Agent

**Dashboard:**
Select "Two-Agent System" in sidebar radio button

**CLI:**
Just select option `2` when prompted
