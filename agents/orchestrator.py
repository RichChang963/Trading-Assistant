"""
Two-Agent Orchestrator - Coordinates between data retrieval and analysis agents
"""
from typing import Dict, Any
from utils.query_router import route_query_to_tool


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
