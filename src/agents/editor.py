import re
from src.llm import get_llm


def _strip_think(text: str) -> str:
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def editor_node(state: dict) -> dict:
    llm = get_llm(temperature=0.1, max_tokens=150)
    draft = state["draft_content"]
    revisions = state.get("revision_count", 0)

    if revisions >= 2:
        return {"is_acceptable": True, "feedback": "Max revisions reached."}

    prompt = f"""/no_think

Review the draft below against two checks:
1. FACTS: Does it include at least one specific number, name, date, or technical detail from the sources — not just generic statements?
2. REFS: Does it include at least one source reference (a URL or a [title](url) link)?

If both are true, it's acceptable.

Example:
Draft: "Rust is known for memory safety without garbage collection, using compile-time ownership checks. Source: [Rust Book](https://doc.rust-lang.org/book/)"
ACCEPTABLE: Yes
FEEDBACK: None

Draft:
{draft}

Output format (exactly):
ACCEPTABLE: Yes or No
FEEDBACK: Short feedback if No, otherwise "None".
"""
    raw = llm.invoke(prompt).content.strip()
    response = _strip_think(raw)  # parse AFTER stripping any thinking content

    print("\n===== RAW EDITOR OUTPUT =====")
    print(response)
    print("================================\n")

    match = re.search(r"ACCEPTABLE:\s*(YES|NO)", response, re.IGNORECASE)
    is_acc = bool(match) and match.group(1).upper() == "YES"

    fb_match = re.search(r"FEEDBACK:\s*(.+)", response, re.IGNORECASE | re.DOTALL)
    feedback = fb_match.group(1).strip() if fb_match else "None"
    if is_acc:
        feedback = "Looks good."

    return {"is_acceptable": is_acc, "feedback": feedback, "revision_count": revisions + 1}