import json
import re
from src.llm import get_llm


def _strip_think(text: str) -> str:
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def reflector_node(state: dict) -> dict:
    llm = get_llm(temperature=0.0, max_tokens=200)
    query = state["original_query"]
    feedback = state["feedback"]

    prompt = f"""/no_think

You are a research assistant. The editor reviewed the draft for the query "{query}" and provided this feedback:
{feedback}

Generate 1 or 2 NEW search queries to find the missing information.
Output ONLY a plain JSON array of strings. Do not add any explanation.

Example format:
["new query 1", "new query 2"]
"""
    raw = llm.invoke(prompt).content.strip()
    response = _strip_think(raw)

    try:
        match = re.search(r"\[[\s\S]*?\]", response)
        queries = json.loads(match.group(0)) if match else [f"{query} {feedback[:100]}"]
        queries = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
        if not queries:
            queries = [f"{query} {feedback[:100]}"]
    except Exception:
        queries = [f"{query} {feedback[:100]}"]

    return {"search_queries": queries[:2]}