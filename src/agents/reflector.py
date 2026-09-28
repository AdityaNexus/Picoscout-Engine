import json
import re
from src.llm import get_llm


def _strip_think(text: str) -> str:
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def reflector_node(state: dict) -> dict:
    llm = get_llm(temperature=0.0, max_tokens=200, thinking=False)
    query = state["original_query"]
    feedback = state["feedback"]

    prompt = f"""/no_think

The editor reviewed a draft for "{query}" and gave this feedback:
{feedback}

Decide: is this MISSING INFORMATION (something the sources didn't cover), or
a WRITING ERROR (a contradiction, or a fact attached to the wrong entity)?

- Missing information → generate 1-2 NEW search queries to find it.
- Writing error → output an empty array. No search fixes it — the writer
  needs to re-read its own draft and the sources it already has.

Output ONLY a JSON array (empty if no search is needed).

Example (missing info):
Feedback: "Missing benchmark numbers comparing throughput."
Output: ["Rust vs Go microservices throughput benchmark"]

Example (writing error):
Feedback: "The memory usage claim under Milvus actually describes Postgres."
Output: []

Feedback: "{feedback}"
Output:
"""
    raw = llm.invoke(prompt).content.strip()
    response = _strip_think(raw)

    try:
        match = re.search(r"\[[\s\S]*?\]", response)
        queries = json.loads(match.group(0)) if match else []
        queries = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
    except Exception:
        queries = []

    return {"search_queries": queries[:2]}