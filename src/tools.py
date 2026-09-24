import json 
from ddgs import DDGS
import wikipedia
import arxiv

def search_duckduckgo(query: str, max_results : int =3)->str:
    try:
        results = list(DDGS().text(query,max_results=max_results))
        formatted = []
        for r in results:
            formatted.append(f"- **Title**: {r.get('title')}\n  **URL**: {r.get('href')}\n  **Snippet**: {r.get('body')}")
        return "\n".join(formatted) if formatted else "No DuckDuckGo results."
    except Exception as e:
        return f"DuckDuckGo error: {str(e)}"



def search_wikipedia(query:str , max_results : int = 1)->str:
    try:
        titles = wikipedia.search(query, results=max_results)
        results = []
        for title in titles:
            try:
                page = wikipedia.page(title,auto_suggest=False)
                results.append(f"- **Title**: {page.title}\n  **URL**: {page.url}\n  **Summary**: {page.summary[:400]}")
            except Exception:
                continue
        return "\n".join(results) if results else "No Wikipedia results."
    except Exception as e:
        return f"Wikipedia error: {str(e)}"



def search_arxiv(query:str , max_results : int = 1)->str:
    try:
        search = arxiv.Search(query = query,max_results = max_results,sort_by = arxiv.SortCriterion.Relevance )
        results = []
        for r in search.results():
            results.append(f"- **Title**: {r.title}\n  **URL**: {r.entry_id}\n  **Summary**: {r.summary[:400]}")
        return "\n".join(results) if results else "No arXiv results."
    except Exception as e:
        return f"arXiv error: {str(e)}"


def execute_research_tools(queries: list[str]) -> list[dict]:
    results = []
    for q in queries:
        ddg = search_duckduckgo(q)
        wiki = search_wikipedia(q)
        arx = search_arxiv(q)
        
        combined = f"### Data for Query: '{q}'\n\n#### DuckDuckGo:\n{ddg}\n\n#### Wikipedia:\n{wiki}\n\n#### ArXiv:\n{arx}\n"
        results.append({"query": q, "content": combined})
    return results