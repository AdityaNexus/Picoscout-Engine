from typing import TypedDict, Annotated
import operator

class ResearchState(TypedDict):
    original_query: str
    search_queries: list[str]
    raw_research_data: Annotated[list[dict], operator.add] # Appends new data
    draft_content: str
    feedback: str
    is_acceptable: bool
    final_output_path: str