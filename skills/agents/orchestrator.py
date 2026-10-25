"""Two-agent orchestrator coordinating data retrieval and analysis.

This module defines orchestrators that route queries, call tools, and format
responses.
"""
from typing import Callable, Dict, Any, List, Optional, TypedDict
import json

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from skills.utils.query_router import route_query_to_tool


class GraphState(TypedDict, total=False):
    user_query: str
    user_id: str
    routing_info: Dict[str, Any]
    memories: List[Dict[str, Any]]
    data_response: str
    tool_outputs: List[Dict[str, str]]
    analysis_response: str
    final_response: str
    error: str
    verbose: bool


class TwoAgentOrchestrator:
    """Orchestrate workflow between data and analysis agents.

    Notes
    -----
    Workflow:
    1. Receive user query.
    2. Route query to determine data needs.
    3. Data agent fetches required data.
    4. Analysis agent analyzes the data.
    5. Return combined result to the user.
    """
    
    def __init__(self, data_agent, analysis_agent):
        """Initialize orchestrator with both agents.

        Parameters
        ----------
        data_agent : object
            Agent specialized in data retrieval.
        analysis_agent : object
            Agent specialized in analysis.
        """
        self.data_agent = data_agent
        self.analysis_agent = analysis_agent
        
    def process_query(self, user_query: str, verbose: bool = True) -> str:
        """Process a user query through both agents.

        Parameters
        ----------
        user_query : str
            User question or request.
        verbose : bool, optional
            Whether to print intermediate steps.

        Returns
        -------
        str
            Final response combining data and analysis.
        """
        if verbose:
            print("\n" + "="*60)
            print("🤖 TWO-AGENT SYSTEM ACTIVATED")
            print("="*60)
        
        # Step 1: Route query to understand data needs
        routing_info = route_query_to_tool(user_query)
        data_query = routing_info['rewritten_query']
        
        if verbose:
            print(f"\n📍 PHASE 1: DATA RETRIEVAL")
            print(f"   Tool suggestion: {routing_info['suggested_tool']}")
            print(f"   Enhanced query: {data_query[:100]}...")
        
        # Step 2: Data agent retrieves data
        try:
            data_result = self.data_agent.invoke({
                "messages": [("user", data_query)]
            })
            data_response = self._extract_message_content(data_result["messages"][-1])
            
            if verbose:
                print(f"\n✅ Data retrieved successfully")
                print(f"   Preview: {data_response[:150]}...")
        except Exception as e:
            return f"❌ Data Retrieval Error: {str(e)}"
        
        # Step 3: Check if data was successfully retrieved
        if "error" in data_response.lower() and "cannot" in data_response.lower():
            return data_response  # Return error message directly
        
        if verbose:
            print(f"\n📊 PHASE 2: DATA ANALYSIS")
            print(f"   Sending data to analysis agent...")
        
        # Step 4: Analysis agent processes the data
        analysis_query = f"""The user asked: "{user_query}"

Here is the data that was retrieved:

{data_response}

Please analyze this data and provide insights addressing the user's question."""
        
        try:
            analysis_result = self.analysis_agent.invoke({
                "messages": [("user", analysis_query)]
            })
            analysis_response = self._extract_message_content(analysis_result["messages"][-1])
            
            if verbose:
                print(f"\n✅ Analysis complete")
        except Exception as e:
            return f"❌ Analysis Error: {str(e)}\n\nRaw Data:\n{data_response}"
        
        # Step 5: Combine results
        if verbose:
            print("\n" + "="*60)
            print("✨ RESPONSE READY")
            print("="*60 + "\n")
        
        # Format final response
        final_response = f"""

{analysis_response}

---
<details>
<summary>📁 View Raw Data</summary>

{data_response}

</details>
"""

        return final_response
    
    def _extract_message_content(self, message) -> str:
        """Extract content from a message object.

        Parameters
        ----------
        message : object
            Message object returned by the agent.

        Returns
        -------
        str
            Extracted text content.
        """
        if hasattr(message, "content"):
            content = message.content
            # Handle list content (like Gemini)
            if isinstance(content, list):
                response = ""
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        response += item["text"]
                    elif isinstance(item, dict) and item.get("type") == "text":
                        response += item.get("text", "")
                    else:
                        response += str(item)
                return response
            return content
        return str(message)


class LangGraphOrchestrator:
    """LangGraph pipeline: route (rewrite query) -> data agent -> recall memory -> analysis agent -> format."""

    MEMORY_LIMIT = 3
    MIN_MEMORY_SIMILARITY = 0.5

    def __init__(
        self,
        data_agent,
        analysis_agent,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        memory_search: Optional[Callable[..., List[Dict[str, Any]]]] = None,
    ):
        self.data_agent = data_agent
        self.analysis_agent = analysis_agent
        self.checkpointer = checkpointer or MemorySaver()
        # memory_search(user_id, query, limit=..., symbol=...) -> [{content, created_at, similarity, ...}]
        self.memory_search = memory_search
        self.graph = self._build_graph()

    def process_query(
        self,
        user_query: str,
        verbose: bool = True,
        session_id: str = "default",
        user_id: str = "local",
    ) -> str:
        return self.response_from_result(
            self.run_query(user_query, verbose=verbose, session_id=session_id, user_id=user_id)
        )

    def run_query(
        self,
        user_query: str,
        verbose: bool = True,
        session_id: str = "default",
        user_id: str = "local",
    ) -> Dict[str, Any]:
        """Run the graph and return the full final state."""
        if verbose:
            print("\n" + "=" * 60)
            print("🤖 TWO-AGENT SYSTEM ACTIVATED")
            print("=" * 60)

        return self.graph.invoke(
            {
                "user_query": user_query,
                "user_id": user_id,
                "verbose": verbose,
            },
            config={"configurable": {"thread_id": session_id}},
        )

    @staticmethod
    def response_from_result(result: Dict[str, Any]) -> str:
        if "final_response" in result:
            return result["final_response"]
        if "error" in result:
            return result["error"]
        return "❌ Unexpected error: missing final response"

    def _build_graph(self):
        builder = StateGraph(GraphState)

        builder.add_node("route_query", self._route_query)
        builder.add_node("data_agent", self._fetch_data)
        builder.add_node("recall_memory", self._recall_memory)
        builder.add_node("analysis", self._analysis)
        builder.add_node("format", self._format_response)

        builder.set_entry_point("route_query")
        builder.add_edge("route_query", "data_agent")
        builder.add_edge("data_agent", "recall_memory")
        builder.add_edge("recall_memory", "analysis")
        builder.add_edge("analysis", "format")
        builder.add_edge("format", END)

        return builder.compile(checkpointer=self.checkpointer)

    def _route_query(self, state: GraphState) -> Dict[str, Any]:
        routing_info = route_query_to_tool(state["user_query"])
        verbose = state.get("verbose", False)

        if verbose:
            print(f"\n📍 PHASE 1: ROUTING")
            print(f"   Tool suggestion: {routing_info.get('suggested_tool')}")
            rewritten = routing_info.get("rewritten_query", "")
            print(f"   Enhanced query: {rewritten[:100]}...")

        return {"routing_info": routing_info}

    def _fetch_data(self, state: GraphState) -> Dict[str, Any]:
        routing_info = state.get("routing_info", {})
        data_query = routing_info.get("rewritten_query") or state["user_query"]

        try:
            result = self.data_agent.invoke({"messages": [("user", data_query)]})
        except Exception as exc:
            return {"data_response": f"❌ Data Retrieval Error: {str(exc)}"}

        messages = result["messages"]
        tool_outputs = [
            {"name": getattr(m, "name", None) or "tool", "content": self._extract_message_content(m)}
            for m in messages
            if getattr(m, "type", None) == "tool"
        ]

        if state.get("verbose", False):
            print(f"\n✅ Data retrieved ({len(tool_outputs)} tool call(s))")

        return {
            "data_response": self._extract_message_content(messages[-1]),
            "tool_outputs": tool_outputs,
        }

    def _recall_memory(self, state: GraphState) -> Dict[str, Any]:
        # Always return the key so a checkpointed thread never reuses the previous turn's memories.
        if self.memory_search is None:
            return {"memories": []}

        params = (state.get("routing_info") or {}).get("parameters") or {}
        try:
            matches = self.memory_search(
                state.get("user_id", "local"),
                state["user_query"],
                limit=self.MEMORY_LIMIT,
                symbol=params.get("symbol"),
            )
        except Exception as exc:
            if state.get("verbose", False):
                print(f"\n⚠️ Memory recall unavailable: {exc}")
            return {"memories": []}

        memories = [m for m in matches if m.get("similarity", 0) >= self.MIN_MEMORY_SIMILARITY]
        if state.get("verbose", False):
            print(f"\n🧠 Recalled {len(memories)} prior analysis(es)")
        return {"memories": memories}

    @staticmethod
    def _format_memories(memories: List[Dict[str, Any]]) -> str:
        blocks = []
        for m in memories:
            created_at = m.get("created_at")
            date = created_at.strftime("%Y-%m-%d") if hasattr(created_at, "strftime") else "unknown date"
            blocks.append(f"[{date}, similarity {m.get('similarity', 0):.2f}]\n{m['content']}")
        return "\n\n---\n\n".join(blocks)

    def _analysis(self, state: GraphState) -> Dict[str, Any]:
        data_response = state.get("data_response", "")
        user_query = state.get("user_query", "")
        verbose = state.get("verbose", False)

        if self._is_data_error(data_response):
            return {"analysis_response": data_response, "error": data_response}

        if verbose:
            print("\n📊 PHASE 2: DATA ANALYSIS")
            print("   Sending data to analysis agent...")

        memories = state.get("memories") or []
        memory_context = (
            "Prior analyses of related questions (may be outdated; the current data "
            "takes precedence, use them only for context and comparison):\n\n"
            f"{self._format_memories(memories)}\n\n"
            if memories
            else ""
        )

        analysis_query = (
            f"The user asked: \"{user_query}\"\n\n"
            "Here is the data that was retrieved:\n\n"
            f"{data_response}\n\n"
            f"{memory_context}"
            "Please analyze this data and provide insights addressing the user's question."
        )

        try:
            analysis_result = self.analysis_agent.invoke(
                {"messages": [("user", analysis_query)]}
            )
            analysis_response = self._extract_message_content(
                analysis_result["messages"][-1]
            )

            if verbose:
                print("\n✅ Analysis complete")
        except Exception as exc:
            return {
                "analysis_response": (
                    f"❌ Analysis Error: {str(exc)}\n\nRaw Data:\n{data_response}"
                )
            }

        return {"analysis_response": analysis_response}

    def _format_response(self, state: GraphState) -> Dict[str, Any]:
        if "error" in state and state["error"]:
            return {"final_response": state["error"]}

        analysis_response = state.get("analysis_response", "")
        tool_outputs = state.get("tool_outputs") or []
        raw_data = "\n\n".join(o["content"] for o in tool_outputs) or state.get("data_response", "")
        final_response = (
            f"{analysis_response}\n\n"
            "---\n"
            "<details>\n"
            "<summary>📁 View Raw Data</summary>\n\n"
            f"{raw_data}\n\n"
            "</details>\n"
        )

        return {"final_response": final_response}

    def _extract_message_content(self, message) -> str:
        if hasattr(message, "content"):
            content = message.content
            if isinstance(content, list):
                response = ""
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        response += item["text"]
                    elif isinstance(item, dict) and item.get("type") == "text":
                        response += item.get("text", "")
                    else:
                        response += str(item)
                return response
            return content
        return str(message)

    def _is_data_error(self, data_response: str) -> bool:
        lower = data_response.lower()
        if "error" in lower and "cannot" in lower:
            return True
        try:
            parsed = json.loads(data_response)
            if isinstance(parsed, dict) and parsed.get("success") is False:
                return True
        except Exception:
            return False
        return False
