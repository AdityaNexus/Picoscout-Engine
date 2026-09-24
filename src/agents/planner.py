import json
import re
from src.llm import get_llm


def planner_node(state: dict) -> dict:
    llm = get_llm(temperature=0.0)

    query = state["original_query"]

    prompt = f"""
You are a research planning agent.

Your task is to decompose the user's research question into
the smallest useful set of independent search queries.

You decide:
- how many queries are needed
- what each query should investigate
- how to combine related aspects

Rules:

1. Identify every important entity, subject, aspect, metric,
   comparison criterion, and use case in the question.

2. Preserve important context from the original question.
   For example, if the question specifies a workload, domain,
   time period, population, or use case, include that context
   in relevant search queries.

3. Do not lose important requirements from the original question.

4. Create focused queries that provide good coverage.

5. Combine related aspects when one query can effectively
   retrieve information for them.

6. Separate aspects when combining them would make the query
   too broad.

7. Do not use a fixed number of queries.
   You decide the appropriate number.

8. Do not create unnecessary duplicate queries.

9. Do not invent information or requirements.

10. Each query must be understandable on its own.

11. Queries should be concise and suitable for web search,
    Wikipedia, or academic search.

12. Do not answer the user's question.

13. Return ONLY a valid JSON array of strings.

User question:
{query}

Output:
"""
    response = llm.invoke(prompt).content.strip()

    try:
        match = re.search(r"\[.*\]", response, re.DOTALL)

        if not match:
            raise ValueError("No JSON array found")

        queries = json.loads(match.group(0))

        if not isinstance(queries, list):
            raise ValueError("Planner output is not a list")

        queries = [
            q.strip()
            for q in queries
            if isinstance(q, str) and q.strip()
        ]

    except Exception as e:
        print(f"Planner error: {e}")
        queries = [query]

    # Remove duplicates while preserving order
    queries = list(dict.fromkeys(queries))

    print("\n===== GENERATED SEARCH QUERIES =====")

    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")

    print(f"\nTotal queries: {len(queries)}")
    print("====================================\n")

    return {
        "search_queries": queries
    }