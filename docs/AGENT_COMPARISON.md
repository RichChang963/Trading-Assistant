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
    
    C --> M[Recall Memory<br/>pgvector]
    M --> D
    
    subgraph D[Analysis Agent]
        D1[Insights<br/>Patterns<br/>Context]
    end
    
    D --> E[Combined Response]
    E --> F[(Neon Postgres)]
    F -.->|research_memories| M
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
<details>
<summary>📁 View Raw Data</summary>

[Expandable section with complete API response]
</details>
```

-----------------------------------------------------

## Example Use Cases

### Best for Two-Agent System

- "Analyze gold price trends over the past year"
- "Compare Apple and Microsoft financial performance"
- "What does the recent CPI data in Germany mean for markets?"

-----------------------------------------------------

## Using the Two-Agent System

**Web app:** start the API and the React frontend, then chat at `http://localhost:5173`. Pick the model provider in the sidebar.

```bash
uv run uvicorn backend.api:app --reload
cd frontend && npm install && npm run dev
```

**CLI:**

```bash
uv run python -m backend.agent_system
```

Both paths save each run (question, answer, raw data, status) to Neon Postgres, and recall the user's similar past analyses as context for new questions. See [MULTI-AGENT_SYSTEM.md](MULTI-AGENT_SYSTEM.md#persistence-neon-postgres).
