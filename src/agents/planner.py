import json
import re

from src.llm import get_llm
PLANNER_PROMPT = """You are a search query decomposition engine for a moderate-scope
research agent — not a deep-research system. Think through the decomposition,
then give your final answer.

GOAL: Convert the user's question into the minimum number of search queries
needed to answer it well.

HARD CONSTRAINTS (never violate these):
- Never output more than 5 queries.
- If the question compares multiple named entities, each entity gets exactly
  ONE query covering all of its relevant attributes together.
- Preserve exact model names, technologies, metrics, versions, and domain terms.
- Final output must be ONLY a JSON object with "entities" (compared subjects,
  empty list if none) and "queries" — no prose before or after it.

Example:
User: Compare Rust and Go for high-concurrency microservices.
Output: {{"entities": ["Rust", "Go"], "queries": ["Rust Tokio async concurrency microservices performance", "Go goroutines channels concurrency microservices performance", "Rust vs Go high concurrency microservices benchmark comparison"]}}

USER QUESTION:
{query}

OUTPUT:
"""

def planner_node(state: dict) -> dict:
    llm = get_llm(max_tokens=1000, thinking=True)  # 300 was sized for no_think; thinking needs headroom
    query = state["original_query"]

    response = llm.invoke(PLANNER_PROMPT.format(query=query)).content.strip()
     # cheap insurance — server should already split this via --reasoning-format

    print("\n===== RAW PLANNER OUTPUT =====")
    print(response)
    print("================================\n")

    try:
        match = re.search(r"\{[\s\S]*\}", response)
        parsed = json.loads(match.group(0))
        entities = [e.strip() for e in parsed.get("entities", []) if isinstance(e, str) and e.strip()]
        queries = list(dict.fromkeys(
            q.strip() for q in parsed.get("queries", []) if isinstance(q, str) and q.strip()
        ))[:5]
    except Exception as e:
        print(f"Planner error: {e}")
        entities, queries = [], [query]

    # unchanged from before — this stays regardless of thinking mode
    covered = {e for e in entities if any(e.lower() in q.lower() for q in queries)}
    for e in entities:
        if e not in covered and len(queries) < 5:
            queries.append(e)

    if not queries:
        queries = [query]

    return {"search_queries": queries, "entities": entities}