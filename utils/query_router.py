import re


def route_query_to_tool(query: str) -> dict:
    """
    Pre-process user queries to suggest the appropriate tool.
    This helps guide the LLM to use tools instead of web search.
    """
    query_lower = query.lower()
    
    # Stock price queries
    if any(word in query_lower for word in ['price', 'stock', 'quote', 'trading']):
        # Extract potential ticker
        ticker_match = re.search(r'\b([A-Z]{1,5})\b', query)
        if ticker_match:
            return {
                "suggested_tool": "get_stock_data or get_yahoo_stock_data",
                "parameters": {"symbol": ticker_match.group(1), "function": "quote"},
                "rewritten_query": f"Use get_stock_data('{ticker_match.group(1)}', 'quote') to answer: {query}"
            }
    
    # Gold/commodities queries
    if 'gold' in query_lower:
        return {
            "suggested_tool": "get_yahoo_stock_data",
            "parameters": {"symbol": "GC=F", "function": "history_1y"},
            "rewritten_query": "Use get_yahoo_stock_data('GC=F', 'history_1y') for gold futures or get_yahoo_stock_data('GLD', 'history_1y') for gold ETF to answer: " + query
        }
    
    # Economic data queries
    if any(word in query_lower for word in ['gdp', 'inflation', 'cpi', 'unemployment', 'economy']):
        return {
            "suggested_tool": "get_economic_data",
            "parameters": {"indicator": "gdp" if "gdp" in query_lower else "cpi"},
            "rewritten_query": f"Use get_economic_data to answer: {query}"
        }
    
    # Market overview queries
    if any(word in query_lower for word in ['market', 'indices', 'gainers', 'losers', 'active']):
        return {
            "suggested_tool": "get_market_overview",
            "rewritten_query": f"Use get_market_overview to answer: {query}"
        }
    
    return {
        "suggested_tool": "unknown",
        "rewritten_query": f"⚠️ IMPORTANT: Only use OpenBB or Yahoo Finance tools to answer: {query}"
    }

def pass_and_return_rewritten_query(user_input: str, agent):
    """Route the user query to suggest tool usage and return the rewritten query response."""
    routing_info = route_query_to_tool(user_input)
    enhanced_input = routing_info['rewritten_query']
    
    print(f"\n[Routing to: {routing_info['suggested_tool']}]")
    
    # Use invoke with enhanced query
    result = agent.invoke({"messages": [("user", enhanced_input)]})
    last_message = result["messages"][-1]

    print("Analyzing...")
    
    # Handle different message formats
    if hasattr(last_message, "content"):
        content = last_message.content
        # If content is a list (like with Gemini), extract text
        if isinstance(content, list):
            response = ""
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    response += item["text"]
                elif (isinstance(item, dict) and "type" in item and 
                    item["type"] == "text"
                ):
                    response += item.get("text", "")
                else:
                    response += str(item)
        else:
            response = content
    else:
        response = str(last_message)
    
    return response
    