import re
from src.llm import get_llm


def _strip_think(text: str) -> str:
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def _trim_evidence(evidence: list[dict], max_items: int = 8) -> list[dict]:
    return sorted(evidence, key=lambda x: x.get("score", 0.0), reverse=True)[:max_items]


def _trim_for_revision(all_evidence: list[dict], new_queries: set,
                       max_items: int = 6, min_new: int = 3) -> list[dict]:
    # Guarantee the newly fetched evidence survives the trim.
    new_items = [e for e in all_evidence if e.get("query") in new_queries]
    old_items = [e for e in all_evidence if e.get("query") not in new_queries]

    new_kept = _trim_evidence(new_items, max_items=min_new) if new_items else []
    old_kept = _trim_evidence(old_items, max_items=max_items - len(new_kept))
    return new_kept + old_kept


def writer_node(state: dict) -> dict:
    llm = get_llm(temperature=0.3, max_tokens=1024)

    query = state["original_query"]
    revision_count = state.get("revision_count", 0)
    feedback = state.get("feedback")
    previous_draft = state.get("draft_content")

    is_revision = bool(revision_count > 0 and feedback and previous_draft)

    # 1. Choose evidence FIRST (this is what was out of order before)
    if is_revision:
        new_queries = set(state.get("search_queries", []))
        evidence = _trim_for_revision(state["raw_research_data"], new_queries)
        has_new = any(e.get("query") in new_queries for e in evidence)

    else:
        new_queries , has_new = set(), False
        evidence = _trim_evidence(state["raw_research_data"])

    def _limit(item:dict)->int:
        if not is_revision:
            return 1200
        if item.get("query") in new_queries:
            return 1200
        return 400 if has_new else 1200
      

    # 2. THEN build the prompt text from that selection
    evidence_blocks = []
    for item in evidence:
        title = item.get("title", "Source")
        url = item.get("url", "")
        content = item.get("content", "").strip()[:_limit(item)]
        if content:
            evidence_blocks.append(f"### Source: [{title}]({url})\n{content}")
    clean_evidence_text = "\n\n---\n\n".join(evidence_blocks)

    if is_revision:
        prompt = f"""/no_think

You are a factual technical writer revising a draft.

USER QUESTION:
{query}

PREVIOUS DRAFT:
{previous_draft}

SEARCH SOURCES:
{clean_evidence_text}

EDITOR FEEDBACK (fix this specifically):
{feedback[:400]}

INSTRUCTIONS:
1. Rewrite the draft so the feedback problem is actually fixed. Do not return the draft unchanged.
2. Keep everything the feedback did NOT flag.
3. Use ONLY facts in the sources above. Copy exact numbers directly.
4. If a detail is still missing, write "Not provided in search results."
5. Do NOT invent, estimate, or guess.
6. Output clean Markdown only. Do NOT add a references/sources section,
   that is added automatically afterward.

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
6. Structure your answer as: one direct sentence answering the question first,
   then supporting details with specific facts from the sources below it.
7. Do NOT add a references/sources section, that is added automatically
   afterward.

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
    return {
        "draft_content": cleaned or "Not provided in search results.",
        "cited_evidence": evidence,  # exactly what the writer saw, revision or not
    }