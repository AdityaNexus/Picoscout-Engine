import re
from src.llm import get_llm


def _strip_think(text: str) -> str:
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def _trim_evidence(evidence: list[dict], max_items: int = 8) -> list[dict]:
    return sorted(evidence, key=lambda x: x.get("score", 0.0), reverse=True)[:max_items]


def writer_node(state: dict) -> dict:
    llm = get_llm(temperature=0.3, max_tokens=1024)

    query = state["original_query"]
    evidence = _trim_evidence(state["raw_research_data"])
    revision_count = state.get("revision_count", 0)
    feedback = state.get("feedback")
    previous_draft = state.get("draft_content")

    evidence_blocks = []
    for item in evidence:
        title = item.get("title", "Source")
        url = item.get("url", "")
        content = item.get("content", "").strip()
        if content:
            evidence_blocks.append(f"### Source: [{title}]({url})\n{content}")
    clean_evidence_text = "\n\n---\n\n".join(evidence_blocks)

    if revision_count > 0 and feedback and previous_draft:
        prompt = f"""/no_think

You are a factual technical writer revising a draft.

USER QUESTION:
{query}

PREVIOUS DRAFT:
{previous_draft}

EDITOR FEEDBACK (fix this specifically):
{feedback}

INSTRUCTIONS:
1. Rewrite the draft to address the feedback above, using the sources below.
2. Keep everything from the previous draft that the feedback did NOT flag.
3. Copy exact numbers, specs, and metrics directly from the sources.
4. If a detail is still missing, write "Not provided in search results."
5. Do NOT invent, estimate, or guess.
6. Output clean Markdown only.

SEARCH SOURCES:
{clean_evidence_text}

REVISED ANSWER:
"""
    else:
        prompt = f"""/no_think

You are a factual technical writer.

USER QUESTION:
{query}

INSTRUCTIONS:
1. Answer using ONLY facts in the sources below.
2. Copy exact numbers, specs, and metrics directly from the sources.
3. If a detail is missing, write "Not provided in search results."
4. Do NOT invent, estimate, or guess.
5. Output clean Markdown only.
6.6. Structure your answer as: one direct sentence answering the question first,
   then supporting details with specific facts from the sources below it.
SEARCH SOURCES:
{clean_evidence_text}

ANSWER:
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    print("\n===== RAW WRITER OUTPUT =====")
    print(raw)
    print("================================\n")

    cleaned = _strip_think(raw)
    return {"draft_content": cleaned or "Not provided in search results."}