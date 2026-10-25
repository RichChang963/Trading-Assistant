# Agent System Architecture

## Overview

The Trading Assistant supports **two-agent system**. The **two-agent system** separates concerns between data retrieval and analysis for better performance and clearer responsibilities.

---------------------------------------------------------

## Architecture

### 🤖🤖 Two-Agent System

```mermaid
graph LR
    A[User Query] --> B[Orchestrator]
    B --> C[Data Agent]
    C -->|retrieves data via tools| M[Recall Memory]
    P[(research_memories<br/>pgvector)] -.->|similar past analyses| M
    M --> D[Analysis Agent]
    D -->|analyzes data| E[Combined Response]
    E -.->|embed + store| P
```

---------------------------------------------------------

## Agents in the Two-Agent System

### 1. Data Agent (`skills/agents/data_agent.py`)

**Purpose**: Fetch market data from APIs

**Responsibilities**:

- ✅ Retrieve requested data using tools
- ✅ Handle commodity symbol mapping (Gold→XAU, Silver→XAG, etc.)
- ✅ Return structured raw data
- ❌ NO analysis or insights

### 2. Analysis Agent (`skills/agents/analysis_agent.py`)

**Purpose**: Analyze financial data and provide insights

**Responsibilities**:

- ✅ Analyze provided data
- ✅ Generate insights and interpretations
- ✅ Provide context and implications
- ❌ NO data fetching (no tools)

### 3. Orchestrator (`skills/agents/orchestrator.py`)

**Purpose**: Coordinate workflow between agents

**Responsibilities**:

1. Receive user query
2. Route query to determine data needs
3. Data agent fetches data
4. Recall similar past analyses from `research_memories`
5. Pass data (and recalled analyses) to analysis agent
6. Combine and return results

`LangGraphOrchestrator` (used by the app) is a LangGraph state graph: `route_query` → `data_agent` → `recall_memory` → `analysis` → `format`. `route_query` (`skills/utils/query_router.py`) only rewrites the question with hints (symbols, countries); the data agent decides which OpenBB tools to call, and every tool call's raw output is kept in `tool_outputs` for the UI and for `api_snapshots`. `TwoAgentOrchestrator` is the same pipeline as a plain class without LangGraph (no checkpointer, no memory recall); the app does not use it.

### 4. Memory Recall (`recall_memory` node)

**Purpose**: Give the analysis agent context from the user's earlier analyses

**How it works**:

- Calls `MemoryRepository().search` (`backend/db/memory.py`), injected into `LangGraphOrchestrator` as `memory_search` by `backend/agent_system.py`
- Embeds the question and runs a pgvector cosine-similarity search over `research_memories`, scoped to the `user_id` and filtered by the routed symbol (e.g. `XAU=F`) when there is one
- Keeps up to `MEMORY_LIMIT` (3) matches with similarity ≥ `MIN_MEMORY_SIMILARITY` (0.5)
- Adds them to the analysis prompt with their dates, marked as background that the current data overrides
- Skips silently (empty `memories`) if no search function is set or the search fails; always resets `memories` so a checkpointed thread never reuses the previous turn's matches

---------------------------------------------------------

## Persistence (Neon Postgres)

Every query goes through `run_analysis` (`backend/db/service.py`). Database failures are logged and never block the answer.

| Storage | Purpose |
|---------|---------|
| `analysis_runs` | Each question and final answer, with status `pending` / `completed` / `failed` |
| `api_snapshots` | Raw output of each data-agent tool call (provider, tool name, symbol, payload) |
| `research_memories` | pgvector (384-dim, `all-MiniLM-L6-v2`) embeddings of completed analyses; searched by `recall_memory` on later questions |
| `user_preferences` | User settings (JSONB) |
| LangGraph checkpoints | Per-thread graph state via the Postgres checkpointer; falls back to in-memory if the DB is unreachable |
| `documents`, `document_chunks`, `chat_sessions`, `chat_messages` | Tables for document RAG and chat history (not yet written by the app) |

The checkpointer (thread state) and pgvector (cross-conversation recall via `recall_memory`) serve different purposes. Create the tables with `uv run python -m backend.db.init_db`.

---------------------------------------------------------

## Benefits of Two-Agent System

### 📊 When to Use

**Use Two-Agent System when**:

- Complex queries requiring deep analysis
- Want transparency in data vs. analysis
- Need to debug data retrieval issues
- Require detailed analytical insights

---------------------------------------------------------

## Example Workflows

### Query: "What is the gold price trend?"

#### Two-Agent System

```txt
1. Orchestrator routes query
2. Data Agent: Fetches XAU=F data via get_stock_data
3. Recall Memory: Finds earlier gold (XAU=F) analyses by this user
4. Analysis Agent: Analyzes price trends, identifies patterns, compares with past analyses
5. Returns: Detailed analysis + raw data (analysis is then embedded into research_memories)
```

---------------------------------------------------------

## File Structure

```txt
Trading-Assistant/
├── backend/
│   ├── agent_system.py        # CLI entry point + LLM setup
│   ├── api.py                 # FastAPI backend (/api/chat, /api/config, /api/docs)
│   └── db/                    # Neon Postgres layer
│       ├── connection.py      # Engine and LangGraph checkpointer
│       ├── models.py          # SQLAlchemy tables
│       ├── repository.py      # analysis_runs / api_snapshots access
│       ├── service.py         # run_analysis: run + persist
│       ├── memory.py          # research_memories add / search
│       ├── embeddings.py      # Embedding model
│       └── init_db.py         # Enable pgvector, create tables
├── frontend/                  # React UI (Vite)
└── skills/                    # AI components
    ├── prompts/               # default system prompts for agents
    ├── agents/
    │   ├── __init__.py        # Module init
    │   ├── data_agent.py      # Data retrieval agent
    │   ├── analysis_agent.py  # Analysis agent
    │   └── orchestrator.py    # Agent coordinator (LangGraph graph incl. recall_memory)
    ├── tools/
    │   └── openbb_tool.py     # OpenBB tools
    └── utils/
        ├── query_router.py    # Query routing & commodity mapping
        └── settings.py        # Prompt loading, country resolution
```

---------------------------------------------------------

## Development

### Adding New Tools

Add the tool in `skills/tools/openbb_tool.py`, then:

- Data agent: add it to the `tools` list in `skills/agents/data_agent.py`.
- Optionally teach `skills/utils/query_router.py` to hint at it.

```python
tools = [
    # existing tools...
    your_new_tool
]
```

### Modifying Analysis Logic

Edit the system prompts of each agent in `skills/prompts/`.

### Tuning Memory Recall

Adjust `MEMORY_LIMIT` and `MIN_MEMORY_SIMILARITY` on `LangGraphOrchestrator` in `skills/agents/orchestrator.py`. To disable recall, construct the orchestrator without `memory_search`.
