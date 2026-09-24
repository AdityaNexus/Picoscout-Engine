import json
import re
from src.llm import get_llm

def planner_node(state: dict) -> dict:
    llm = get_llm(temperature=0.0)
    query = state["original_query"]
    
    prompt = f"""Break down the following research question into 2 or 3 precise search queries.
Question: {query}

Output ONLY a plain JSON array of strings. Do not add any explanation or preamble.
Example format:
["query 1", "query 2"]
"""
    response = llm.invoke(prompt).content.strip()
    
    try:
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            queries = json.loads(match.group(0))
        else:
            queries = [query]
    except Exception:
        queries = [query]
        
    return {"search_queries": queries[:3]}