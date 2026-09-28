import re
from src.llm import get_llm


def _strip_think(text: str) -> str:
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def editor_node(state: dict) -> dict:
    llm = get_llm(temperature=0.6, max_tokens=700, thinking=True)  # no /no_think — reasoning helps here
    draft = state["draft_content"]

    prompt = f"""Review the draft below for two things:

1. FACTUAL CONTENT: Does it contain specific facts (numbers, names, technical
   details) from the sources, not vague or generic statements?
2. INTERNAL CONSISTENCY: Does any claim contradict another claim elsewhere in
   the draft, or does a fact filed under one system/entity actually look like
   it belongs to a different one?

If either problem exists, it's NOT acceptable — point to the specific
sentence(s) so the writer knows exactly what to fix.

Draft:
{draft}

Give your reasoning, then finish with exactly this format:
ACCEPTABLE: Yes or No
FEEDBACK: Short, specific feedback if No, otherwise "None".
"""
    raw = llm.invoke(prompt).content.strip()
    response = _strip_think(raw)

    print("\n===== RAW EDITOR OUTPUT =====")
    print(response)
    print("================================\n")

    match = re.search(r"ACCEPTABLE:\s*(YES|NO)", response, re.IGNORECASE)
    is_acc = bool(match) and match.group(1).upper() == "YES"
    fb_match = re.search(r"FEEDBACK:\s*(.+)", response, re.IGNORECASE | re.DOTALL)
    feedback = fb_match.group(1).strip() if fb_match else "None"
    if is_acc:
        feedback = "Looks good."

    # revision_count=1 unconditionally: harmless when accepted (exporter next
    # either way), and it's what tells route_after_writer to skip editor on
    # the second writer call if this draft got rejected.
    return {"is_acceptable": is_acc, "feedback": feedback, "revision_count": 1}