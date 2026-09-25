import os
import re
from datetime import datetime

from langgraph.graph import StateGraph, END

from src.state import ResearchState
from src.agents.planner import planner_node
from src.agents.writer import writer_node
from src.agents.editor import editor_node
from src.tools import execute_research_tools


# ---------------------------------------------------------
# RESEARCHER NODE
# ---------------------------------------------------------

def research_node(state: ResearchState):
    queries = state["search_queries"]

    results = execute_research_tools(queries)

    print("\n===== RESEARCH RESULTS =====")
    print(f"Queries: {len(queries)}")
    print(f"Evidence items: {len(results)}")

    for i, item in enumerate(results[:10], 1):
        print(
            f"{i}. "
            f"[{item.get('source')}] "
            f"{item.get('title')}"
        )

    print("============================\n")

    return {
        "raw_research_data": results
    }


# ---------------------------------------------------------
# EXPORTER NODE
# ---------------------------------------------------------

def exporter_node(state: dict) -> dict:
    os.makedirs("outputs", exist_ok=True)
    query = state["original_query"]

    content = f"# Research Report: {query}\n\n"
    content += state["draft_content"]

    verdict = state.get("is_acceptable")
    feedback = state.get("feedback")
    if verdict is not None:
        content += f"\n\n---\n*Editor verdict: {'✅ Accepted' if verdict else '❌ Needs revision'} — {feedback}*"

    print("\n" + "=" * 60)
    print("📝 FINAL RESEARCH DRAFT")
    print("=" * 60)
    print(content)
    print("=" * 60 + "\n")
    # ... rest unchanged

    # Create safe filename
    safe_query = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        query.replace(" ", "_")
    )

    safe_query = safe_query[:30].strip("_")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"outputs/report_{safe_query}_{timestamp}.md"

    # Save report
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "final_output_path": filename
    }


# ---------------------------------------------------------
# BUILD GRAPH
# ---------------------------------------------------------

def build_graph():

    builder = StateGraph(ResearchState)

    # Nodes
    builder.add_node("planner", planner_node)
    builder.add_node("researcher", research_node)
    builder.add_node("writer", writer_node)
    builder.add_node("editor", editor_node)
    builder.add_node("exporter", exporter_node)

    # Entry
    builder.set_entry_point("planner")

    # Main pipeline
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "editor")

    # For now, ALWAYS export after editor.
    # We are testing Writer quality, so don't trigger
    # reflection/research loops yet.
    builder.add_edge("editor", "exporter")

    # Finish
    builder.add_edge("exporter", END)

    return builder.compile()