from src.graph import build_graph

def main():
    graph = build_graph()
    
    query = input("Enter your research topic: ").strip()
    if not query:
        query = "Latest developments in agentic AI frameworks"
        
    initial_state = {
        "original_query": query,
        "search_queries": [],
        "raw_research_data": [],
        "draft_content": "",
        "feedback": "",
        "revision_count": 0,
        "is_acceptable": False,
        "final_output_path": ""
    }
    
    print(f"\n🚀 Starting Research Graph for: '{query}'...\n")
    
    for event in graph.stream(initial_state,stream_mode = "updates"):
        for node_name, output in event.items():
            print(f"--- Completed Node: {node_name} ---")
            if node_name == "planner":
                print(f"Generated Queries: {output.get('search_queries')}")
            elif node_name == "editor":
                print(f"Accepted: {output.get('is_acceptable')}")
                if not output.get('is_acceptable'):
                    print(f"Feedback: {output.get('feedback')}")
                print(f"final output\n: {output.get('draft_content')}\n")
            elif node_name == "exporter":
                print(f"\n✅ Report generated successfully!")
                print(f"Saved to: {output.get('final_output_path')}\n")
               
          
if __name__ == "__main__":
    main()