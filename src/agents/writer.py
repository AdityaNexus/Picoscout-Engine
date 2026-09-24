from src.llm import get_llm

def writer_node(state: dict) -> dict:
    llm = get_llm(temperature=0.2)
    query = state["original_query"]
    data = "\n\n".join([item["content"] for item in state["raw_research_data"]])
    
    prompt = f"""You are an expert academic researcher. Write a detailed research summary answering the user query based ONLY on the provided research data.

User Query: {query}

Research Data:
{data}

Requirements:
1. Synthesize the facts clearly under logical headings.
2. Include inline citations with URLs from the sources provided in the data (e.g., [Source Name](URL)).
3. Add a dedicated "### References" section at the end listing all URLs used.
"""
    draft = llm.invoke(prompt).content
    return {"draft_content": draft}