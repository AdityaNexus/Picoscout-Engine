import os
import re
from datetime import datetime
from langgraph.graph import StateGraph, END
from src.state import ResearchState
from src.agents.planner import planner_node
from src.agents.writer import writer_node
from src.agents.editor import editor_node
from src.tools import execute_research_tools
from src.agents.refelctor import reflector_node

def tool_execution_node(state : dict)->dict:
    queries = state.get("search_queries", [])
    results = execute_research_tools(queries)
    return {"raw_research_data": results}

def exporter_node(state: dict) -> dict:
    os.makedirs("outputs", exist_ok=True)
    
    query = state['original_query']
    content = f"# Research Report: {query}\n\n"
    content += state["draft_content"]
    
    # 1. Print the final result to the terminal before exporting
    print("\n" + "="*60)
    print("📝 FINAL RESEARCH DRAFT")
    print("="*60)
    print(content)
    print("="*60 + "\n")
    
    # 2. Generate a unique filename using the query and a timestamp
    # Replace spaces with underscores and remove any special characters
    safe_query = re.sub(r'[^a-zA-Z0-9_\-]', '_', query.replace(' ', '_'))
    # Keep it to a reasonable length (e.g., first 30 characters)
    safe_query = safe_query[:30].strip('_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"outputs/report_{safe_query}_{timestamp}.md"
    
    # 3. Save the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
        
    return {"final_output_path": filename}


def route_editor(state: dict) -> str:
    if state.get("is_acceptable", False):
        return "exporter"
    return "reflector"  # If not acceptable, go to reflector for new queries

def route_writer(state: dict) -> str:
    if state.get("revision_count", 0) >0:
        return "exporter"
    return "editor"

def build_graph():
    builder = StateGraph(ResearchState)
    
    builder.add_node("planner", planner_node)
    builder.add_node("researcher", tool_execution_node)
    builder.add_node("writer", writer_node)
    builder.add_node("editor", editor_node)
    builder.add_node("reflector", reflector_node)
    builder.add_node("exporter", exporter_node)
    
    builder.set_entry_point("planner")
    
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "editor")
    
    builder.add_conditional_edges(
        "editor",
        route_editor,
        {
            "exporter": "exporter",
            "planner": "planner"
        }
    )

    builder.add_conditional_edges(
        "editor",
        route_writer,
        {
            "exporter": "exporter",
            "reflector": "reflector"
        }
    )
    
    builder.add_edge("exporter", END)
    return builder.compile()