import os
import re
from datetime import datetime
import time
from langgraph.graph import StateGraph, END

from src.state import ResearchState
from src.agents.planner import planner_node
from src.agents.writer import writer_node
from src.agents.editor import editor_node
from src.agents.reflector import reflector_node
from src.tools import execute_research_tools

def timed(name, fn):
    def wrapper(state):
        t = time.perf_counter()
        out = fn(state)
        print(f"⏱ {name}: {time.perf_counter() - t:.1f}s")
        return out
    return wrapper

def research_node(state: ResearchState):
    queries = state["search_queries"]
    results = execute_research_tools(queries)

    print("\n===== RESEARCH RESULTS =====")
    print(f"Queries: {len(queries)}")
    print(f"Evidence items: {len(results)}")
    for i, item in enumerate(results[:10], 1):
        print(f"{i}. [{item.get('source')}] {item.get('title')}")
    print("============================\n")

    return {"raw_research_data": results}


def exporter_node(state: dict) -> dict:
    os.makedirs("outputs", exist_ok=True)
    query = state["original_query"]
    evidence = state.get("cited_evidence", [])

    content = f"# Research Report: {query}\n\n"
    content += state["draft_content"]

    seen = set()
    refs = []
    for item in evidence:
        url = item.get("url", "").strip()
        title = item.get("title", "Source").strip()
        if url and url not in seen:
            seen.add(url)
            refs.append(f"- [{title}]({url})")
    if refs:
        content += "\n\n## References\n\n" + "\n".join(refs)

    revision_count = state.get("revision_count", 0)
    verdict = state.get("is_acceptable")
    feedback = state.get("feedback")

    if revision_count > 0:
        # A revision happened AFTER this verdict was recorded — the stored
        # verdict reflects the pre-revision draft, not what's being exported.
        note = f"*Editor flagged the first draft ({feedback}) — one revision was made and exported without a second review.*"
    elif verdict is not None:
        note = f"*Editor verdict: {'✅ Accepted' if verdict else '❌ Needs revision'} — {feedback}*"
    else:
        note = None
    if note:
        content += f"\n\n---\n{note}"

    print("\n" + "=" * 60)
    print("📝 FINAL RESEARCH DRAFT")
    print("=" * 60)
    print(content)
    print("=" * 60 + "\n")

    safe_query = re.sub(r"[^a-zA-Z0-9_-]", "_", query.replace(" ", "_"))
    safe_query = safe_query[:30].strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/report_{safe_query}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return {"final_output_path": filename}


def route_after_writer(state: dict) -> str:

    return "editor" if state.get("revision_count", 0) == 0 else "exporter"


def route_after_editor(state: dict) -> str:
    return "exporter" if state.get("is_acceptable") else "reflector"


def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("planner", timed("planner", planner_node))
    builder.add_node("researcher", timed("researcher", research_node))
    builder.add_node("writer", timed("writer", writer_node))
    builder.add_node("editor", timed("editor", editor_node))
    builder.add_node("reflector", timed("reflector", reflector_node))
    builder.add_node("exporter", timed("exporter", exporter_node))

    builder.set_entry_point("planner")

    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "writer")

    builder.add_conditional_edges(
        "writer", route_after_writer, {"editor": "editor", "exporter": "exporter"}
    )
    builder.add_conditional_edges(
        "editor", route_after_editor, {"exporter": "exporter", "reflector": "reflector"}
    )
    builder.add_edge("reflector", "researcher")
    builder.add_edge("exporter", END)

    return builder.compile()