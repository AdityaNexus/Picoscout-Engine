import json 
import re

from src.llm import get_llm

def planner_node(state:dict)->dict:
    llm = get_llm(temperature=0.1)
    query = state["original_query"]
    
    prompt = f"""
You are a research query analyzer.

Analyze the user's research question and identify:

1. ENTITIES:
   The main subjects, technologies, products, people, organizations,
   concepts, or things that need to be researched.

2. RESEARCH_ASPECTS:
   The specific properties, topics, criteria, or dimensions that
   the user wants to investigate or compare.

Rules:

- Do NOT answer the question.
- Do NOT provide factual information.
- Do NOT invent specifications, numbers, dates, or claims.
- Extract only what is required to research the question.
- If the question is comparative, identify ALL important comparison aspects.
- If the question is not comparative, identify the major research aspects.
- Do not force exactly 3 items.
- Keep each item short.
- Avoid duplicates.

Return ONLY valid JSON in exactly this structure:

{{
  "entities": ["...", "..."],
  "research_aspects": ["...", "..."]
}}

User question:
{query}
"""
    response = llm.invoke(prompt).content.strip()
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if not match:
            raise ValueError("No JSON object found in the response.")

        plan = json.loads(match.group(0))

        entities  = plan.get("entities", [])
        aspects = plan.get("research_aspects", [])


        if not isinstance(entities,list):
            raise ValueError("Entities is not a list.")
        if not isinstance(aspects,list):
            raise ValueError("Research aspects is not a list.")

    except Exception :
        entities = [query]
        aspects = ["overview"]


    entities = list(dict.fromkeys(entities))
    aspects = list(dict.fromkeys(aspects))

    search_queries = []

    for entity in entities:
        for aspect in aspects:
            search_queries.append(f"{entity} {aspect}")

    search_queries = list(dict.fromkeys(search_queries))

    return {
        "entities": entities,
        "research_aspects": aspects,
        "search_queries": search_queries
    }