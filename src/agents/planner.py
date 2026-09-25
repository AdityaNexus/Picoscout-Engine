import json
import re

from src.llm import get_llm


def planner_node(state: dict) -> dict:

    # Planner does NOT need a reasoning model to think extensively.
    llm = get_llm(
        temperature=0.0,
        max_tokens=300
    )

    query = state["original_query"]

        PLANNER_PROMPT = """/no_think

You are a search query decomposition engine.

Your ONLY task is to convert the user's question into
the minimum number of search queries required to answer it.

RULES:

1. Generate between 1 and 5 queries. This is a hard limit — NEVER exceed 5,
   even for complex multi-part or multi-entity questions.
2. Generate ONLY necessary queries.
3. Simple questions usually require 1 query.
4. When comparing MULTIPLE entities across MULTIPLE attributes, combine ALL
   attributes for ONE entity into a SINGLE query. Do NOT create a separate
   query per attribute — that causes query explosion and is not allowed.
5. Preserve model names, technologies, metrics, versions, algorithms, and
   important domain terminology.
6. Each query must be useful as an independent search query.
7. Do NOT explain your reasoning, generate answers, or generate markdown.
8. Output ONLY a valid JSON array of strings.

Example (2 entities):

User:
Compare Rust and Go for high-concurrency microservices.

Output:
[
  "Rust Tokio async concurrency microservices performance",
  "Go goroutines channels concurrency microservices performance",
  "Rust vs Go high concurrency microservices benchmark comparison"
]

Example (3 entities, 3 attributes — each entity's attributes are combined
into ONE query, not split per attribute):

User:
Compare AWS Lambda, GCP Cloud Functions, and Azure Functions for serverless
compute: cold start latency, pricing, and max execution duration.

Output:
[
  "AWS Lambda cold start latency pricing max execution duration",
  "GCP Cloud Functions cold start latency pricing max execution duration",
  "Azure Functions cold start latency pricing max execution duration",
  "AWS Lambda vs GCP Cloud Functions vs Azure Functions serverless benchmark comparison"
]

User:
How does ChromaDB work?

Output:
[
  "ChromaDB vector database architecture embeddings retrieval"
]

USER QUESTION:
{query}

OUTPUT:
"""
    try:

        response = llm.invoke(
            PLANNER_PROMPT.format(query=query)
        ).content.strip()

        print("\n===== RAW PLANNER OUTPUT =====")
        print(response)
        print("================================\n")

        # Find first JSON array.
        match = re.search(
            r"\[[\s\S]*?\]",
            response
        )

        if not match:
            raise ValueError(
                "Planner did not return a JSON array"
            )

        queries = json.loads(match.group(0))

        if not isinstance(queries, list):
            raise ValueError(
                "Planner output is not a list"
            )

        # Validate + clean
        cleaned = []

        for q in queries:

            if not isinstance(q, str):
                continue

            q = q.strip()

            if not q:
                continue

            cleaned.append(q)

        # Hard safety limit
        queries = cleaned[:5]

        # Remove duplicates
        queries = list(dict.fromkeys(queries))

        # Never allow empty planner output
        if not queries:
            queries = [query]

    except Exception as e:

        print(f"Planner error: {e}")

        # Safe fallback
        queries = [query]

    print("\n===== GENERATED SEARCH QUERIES =====")

    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")

    print(f"\nTotal queries: {len(queries)}")
    print("====================================\n")

    return {
        "search_queries": queries
    }