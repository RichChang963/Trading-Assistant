import re


def route_query_to_tool(query: str) -> dict:
    """
    Pre-process user queries to suggest the appropriate tool.
    This helps guide the LLM to use tools instead of web search.
    """
    query_lower = query.lower()
    
    # Commodity mapping: keyword -> [primary_symbol, alternatives...]
    commodity_map = {
        "gold": ["XAU=F", "GC=F", "GLD"],
        "xau": ["XAU=F", "GC=F", "GLD"],
        "silver": ["XAG=F", "SI=F", "SLV"],
        "xag": ["XAG=F", "SI=F", "SLV"],
        "oil": ["CL=F", "BZ=F", "USO"],
        "crude": ["CL=F", "BZ=F", "USO"],
        "wti": ["CL=F"],
        "brent": ["BZ=F"],
        "natural gas": ["NG=F", "UNG"],
        "copper": ["HG=F", "COPX"],
        "platinum": ["PL=F", "PPLT"],
        "palladium": ["PA=F", "PALL"],
        "corn": ["ZC=F", "CORN"],
        "wheat": ["ZW=F", "WEAT"],
        "soybean": ["ZS=F", "SOYB"],
        "cotton": ["CT=F"],
        "coffee": ["KC=F"],
        "sugar": ["SB=F"],
    }
    
    # Check for commodity keywords FIRST (before generic stock queries)
    for commodity, symbols in commodity_map.items():
        if commodity in query_lower:
            primary = symbols[0]
            alternatives = ', '.join([f"'{s}'" for s in symbols[1:]])
            
            suggestion = f"IMMEDIATELY call get_stock_data('{primary}', 'quote') to get current {commodity} price data. "
            if alternatives:
                suggestion += f"Alternative symbols if needed: {alternatives}. "
            suggestion += f"Then analyze the data. User query: {query}"
            
            return {
                "suggested_tool": "get_stock_data",
                "parameters": {"symbol": primary, "function": "quote"},
                "rewritten_query": suggestion
            }
    
    # Stock price queries
    if any(word in query_lower for word in ['price', 'stock', 'quote', 'trading']):
        # Extract potential ticker
        ticker_match = re.search(r'\b([A-Z]{1,5})\b', query)
        if ticker_match:
            ticker = ticker_match.group(1)
            return {
                "suggested_tool": "get_stock_data",
                "parameters": {"symbol": ticker, "function": "quote"},
                "rewritten_query": f"IMMEDIATELY call get_stock_data('{ticker}', 'quote') to fetch current data, then analyze it. User query: {query}"
            }
    
    # Economic data queries
    if any(word in query_lower for word in ['gdp', 'inflation', 'cpi', 'unemployment', 'economy', 'interest rate']):
        # Determine specific indicator
        if 'gdp' in query_lower:
            indicator = 'gdp'
        elif 'cpi' in query_lower or 'inflation' in query_lower:
            indicator = 'cpi'
        elif 'unemployment' in query_lower:
            indicator = 'unemployment'
        elif 'interest' in query_lower or 'rate' in query_lower:
            indicator = 'interest_rate'
        else:
            indicator = 'cpi'  # default to CPI
        
        return {
            "suggested_tool": "get_economic_data",
            "parameters": {"indicator": indicator, "country": "USA"},
            "rewritten_query": f"IMMEDIATELY call get_economic_data('{indicator}', 'USA') to fetch current data, then analyze it. User query: {query}"
        }
    
    # Market overview queries
    if any(word in query_lower for word in ['market', 'indices', 'gainers', 'losers', 'active']):
        # Determine specific data type
        if 'indices' in query_lower or 'index' in query_lower:
            data_type = 'indices'
        elif 'gainer' in query_lower:
            data_type = 'gainers'
        elif 'loser' in query_lower:
            data_type = 'losers'
        elif 'active' in query_lower:
            data_type = 'active'
        elif 'sector' in query_lower:
            data_type = 'sectors'
        else:
            data_type = 'indices'  # default to indices for general "market" queries
        
        return {
            "suggested_tool": "get_market_overview",
            "parameters": {"data_type": data_type},
            "rewritten_query": f"IMMEDIATELY call get_market_overview('{data_type}') to fetch current data, then analyze it. User query: {query}"
        }
    
    return {
        "suggested_tool": "unknown",
        "rewritten_query": f"⚠️ IMPORTANT: Only use OpenBB tools to answer: {query}"
    }

def pass_and_return_rewritten_query(user_input: str, agent):
    """Route the user query to suggest tool usage and return the rewritten query response."""
    routing_info = route_query_to_tool(user_input)
    enhanced_input = routing_info['rewritten_query']
    
    print(f"\n[Routing to: {routing_info['suggested_tool']}]")

    # Use invoke with enhanced query
    result = agent.invoke({
        "messages": [{"role": "user", "content": enhanced_input}]
    })
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
    