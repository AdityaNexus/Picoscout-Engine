import json
import re
from src.llm import get_llm

def reflector_node(state: dict) -> dict:
    llm = get_llm(temperature=0.1)
    query = state["original_query"]
    feedback = state["feedback"]
    
    prompt = f"""You are a research assistant. The editor reviewed the draft for the query "{query}" and provided this feedback:
{feedback}

Generate 1 or 2 NEW search queries to find the missing information. 
Output ONLY a plain JSON array of strings. Do not add any explanation.
Example format:
["new query 1", "new query 2"]
"""
    response = llm.invoke(prompt).content.strip()
    
    # Robust parsing for 0.6B models
    try:
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            queries = json.loads(match.group(0))
        else:
            queries = [f"{query} {feedback}"]
    except Exception:
        queries = [f"{query} {feedback}"]
        
    # We replace the search_queries list so the researcher only searches the new ones.
    # The researcher node uses operator.add for raw_research_data, so old data is kept.
    return {"search_queries": queries[:2]}