"""
Two-Agent Orchestrator - Coordinates between data retrieval and analysis agents
"""
from typing import Dict, Any, Optional, TypedDict
import json

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from utils.query_router import route_query_to_tool
from tools.openbb_tool import (
    get_stock_data,
    get_economic_data,
    get_market_overview,
)


class GraphState(TypedDict, total=False):
    user_query: str
    routing_info: Dict[str, Any]
    data_response: str
    analysis_response: str
    final_response: str
    error: str
    verbose: bool


class TwoAgentOrchestrator:
    """
    Orchestrates workflow between data agent and analysis agent.
    
    Workflow:
    1. Receive user query
    2. Route query to determine data needs
    3. Data agent fetches required data
    4. Analysis agent analyzes the data
    5. Return combined result to user
    """
    
    def __init__(self, data_agent, analysis_agent):
        """
        Initialize orchestrator with both agents.
        
        Args:
            data_agent: Agent specialized in data retrieval
            analysis_agent: Agent specialized in analysis
        """
        self.data_agent = data_agent
        self.analysis_agent = analysis_agent
        
    def process_query(self, user_query: str, verbose: bool = True) -> str:
        """
        Process user query through both agents.
        
        Args:
            user_query: User's question or request
            verbose: Whether to print intermediate steps
            
        Returns:
            Final response combining data and analysis
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
        final_response = f"""## 📊 Analysis Results

{analysis_response}

---
<details>
<summary>📁 View Raw Data</summary>

{data_response}

</details>
"""
        
        return final_response
    
    def _extract_message_content(self, message) -> str:
        """Extract content from message object."""
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
    """
    LangGraph-based orchestrator that routes, calls tools, and analyzes data.
    """

    def __init__(self, analysis_agent, checkpointer: Optional[MemorySaver] = None):
        self.analysis_agent = analysis_agent
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = self._build_graph()

    def process_query(
        self,
        user_query: str,
        verbose: bool = True,
        session_id: str = "default",
    ) -> str:
        if verbose:
            print("\n" + "=" * 60)
            print("🤖 LANGGRAPH TWO-AGENT SYSTEM ACTIVATED")
            print("=" * 60)

        result = self.graph.invoke(
            {
                "user_query": user_query,
                "verbose": verbose,
            },
            config={"configurable": {"thread_id": session_id}},
        )

        if "final_response" in result:
            return result["final_response"]
        if "error" in result:
            return result["error"]
        return "❌ Unexpected error: missing final response"

    def _build_graph(self):
        builder = StateGraph(GraphState)

        builder.add_node("route_query", self._route_query)
        builder.add_node("tool_stock", self._tool_stock)
        builder.add_node("tool_economic", self._tool_economic)
        builder.add_node("tool_market", self._tool_market)
        builder.add_node("tool_unknown", self._tool_unknown)
        builder.add_node("analysis", self._analysis)
        builder.add_node("format", self._format_response)

        builder.set_entry_point("route_query")
        builder.add_conditional_edges(
            "route_query",
            self._select_tool,
            {
                "get_stock_data": "tool_stock",
                "get_economic_data": "tool_economic",
                "get_market_overview": "tool_market",
                "unknown": "tool_unknown",
            },
        )
        builder.add_edge("tool_stock", "analysis")
        builder.add_edge("tool_economic", "analysis")
        builder.add_edge("tool_market", "analysis")
        builder.add_edge("tool_unknown", "analysis")
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

    def _select_tool(self, state: GraphState) -> str:
        routing_info = state.get("routing_info", {})
        suggested_tool = routing_info.get("suggested_tool", "unknown")
        if suggested_tool in {
            "get_stock_data",
            "get_economic_data",
            "get_market_overview",
        }:
            return suggested_tool
        return "unknown"

    def _tool_stock(self, state: GraphState) -> Dict[str, Any]:
        return self._call_tool(get_stock_data, state)

    def _tool_economic(self, state: GraphState) -> Dict[str, Any]:
        return self._call_tool(get_economic_data, state)

    def _tool_market(self, state: GraphState) -> Dict[str, Any]:
        return self._call_tool(get_market_overview, state)

    def _tool_unknown(self, state: GraphState) -> Dict[str, Any]:
        return {
            "data_response": (
                "❌ Data Retrieval Error: No suitable tool available for this query."
            )
        }

    def _call_tool(self, tool, state: GraphState) -> Dict[str, Any]:
        routing_info = state.get("routing_info", {})
        parameters = routing_info.get("parameters", {})
        verbose = state.get("verbose", False)

        if verbose:
            print(f"\n📍 PHASE 1: DATA RETRIEVAL")
            print(f"   Tool call: {routing_info.get('suggested_tool')}")

        try:
            if hasattr(tool, "invoke"):
                tool_result = tool.invoke(parameters)
            else:
                tool_result = tool(**parameters)
        except Exception as exc:
            return {"data_response": f"❌ Data Retrieval Error: {str(exc)}"}

        data_response = self._ensure_text(tool_result)

        if verbose:
            print("\n✅ Data retrieved successfully")
            print(f"   Preview: {data_response[:150]}...")

        return {"data_response": data_response}

    def _analysis(self, state: GraphState) -> Dict[str, Any]:
        data_response = state.get("data_response", "")
        user_query = state.get("user_query", "")
        verbose = state.get("verbose", False)

        if self._is_data_error(data_response):
            return {"analysis_response": data_response, "error": data_response}

        if verbose:
            print("\n📊 PHASE 2: DATA ANALYSIS")
            print("   Sending data to analysis agent...")

        analysis_query = (
            f"The user asked: \"{user_query}\"\n\n"
            "Here is the data that was retrieved:\n\n"
            f"{data_response}\n\n"
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
        data_response = state.get("data_response", "")

        final_response = (
            "## 📊 Analysis Results\n\n"
            f"{analysis_response}\n\n"
            "---\n"
            "<details>\n"
            "<summary>📁 View Raw Data</summary>\n\n"
            f"{data_response}\n\n"
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

    def _ensure_text(self, tool_result: Any) -> str:
        if isinstance(tool_result, str):
            return tool_result
        try:
            return json.dumps(tool_result, indent=2, default=str)
        except TypeError:
            return str(tool_result)

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
