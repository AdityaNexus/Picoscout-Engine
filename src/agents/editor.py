from src.llm import get_llm

def editor_node(state: dict) -> dict:
    llm = get_llm(temperature=0.0)
    draft = state["draft_content"]
    revisions = state.get("revision_count", 0)
    
    # Cap revisions at 2 so 0.6B models don't get stuck in infinite loops
    if revisions >= 2:
        return {"is_acceptable": True, "feedback": "Max revisions reached."}
    
    prompt = f"""Review the following draft for two things:
1. Does it directly answer the topic?
2. Does it contain references/links?

Draft:
{draft}

Output format:
ACCEPTABLE: Yes or No
FEEDBACK: Short feedback if No.
"""
    response = llm.invoke(prompt).content
    
    is_acc = "ACCEPTABLE: YES" in response.upper() or "YES" in response.split("\n")[0].upper()
    feedback = response.split("FEEDBACK:")[-1].strip() if not is_acc else "Looks good."
    
    return {
        "is_acceptable": is_acc, 
        "feedback": feedback, 
        "revision_count": revisions + 1
    }