import os
import wikipedia
import arxiv
from tavily import TavilyClient
from dotenv import load_dotenv
from ddgs import DDGS
load_dotenv()
from concurrent.futures import ThreadPoolExecutor, as_completed

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ============================================================
# Tavily
# ============================================================

def search_duckduckgo(query: str, max_results: int = 1) -> list[dict]:
    try:
        results = list(DDGS().text(query, max_results=max_results))
        formatted = []
        for item in results:
            formatted.append({
                "source": "duckduckgo",
                "title": item.get("title", "").strip(),
                "url": item.get("href", "").strip(),    # ddgs key is "href", not "url"
                "content": item.get("body", "").strip(),  # ddgs key is "body", not "content"
                "score": 0.0,  # text() has no relevance score
            })
        return formatted
    except Exception as e:
        print(f"DuckDuckGo search error for '{query}': {e}")
        return []

def search_tavily(query: str, max_results: int = 3) -> list[dict]:
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False
        )

        results = []
        for item in response.get("results", []):
            content = item.get("content", "").strip()
            if not content:
                continue

            results.append({
                "source": "tavily",
                "title": item.get("title", "").strip(),
                "url": item.get("url", "").strip(),
                "content": content[:1200],  # Limit content to first 1200 chars
                "score": item.get("score", 0.0),
            })
        return results

    except Exception as e:
        print(f"Tavily search error for '{query}': {e}")
        return []


# ============================================================
# Wikipedia
# ============================================================

def search_wikipedia(query: str, max_results: int = 1) -> list[dict]:
    try:
        titles = wikipedia.search(query, results=max_results)
        results = []

        for title in titles:
            try:
                page = wikipedia.page(title, auto_suggest=False, redirect=True)
                content = page.summary.strip()
                if not content:
                    continue

                results.append({
                    "source": "wikipedia",
                    "title": page.title,
                    "url": page.url,
                    "content": content[:1000],
                    "score": 0.0,
                })

            except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
                continue
            except Exception as e:
                print(f"Wikipedia page error for '{title}': {e}")
                continue

        return results

    except Exception as e:
        print(f"Wikipedia search error for '{query}': {e}")
        return []


# ============================================================
# arXiv
# ============================================================

def search_arxiv(query: str, max_results: int = 1) -> list[dict]:
    try:
        client = arxiv.Client(page_size=max_results, delay_seconds=2, num_retries=2)
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = []
        for paper in client.results(search):
            results.append({
                "source": "arxiv",
                "title": paper.title.strip(),
                "url": paper.entry_id,
                "content": paper.summary.strip()[:1000],
                "score": 0.0,
            })

        return results

    except Exception as e:
        print(f"arXiv search error for '{query}': {e}")
        return []


# ============================================================
# Evidence Cleanup
# ============================================================

def clean_evidence(results: list[dict]) -> list[dict]:
    cleaned = []
    seen_urls = set()

    for item in results:
        content = item.get("content", "").strip()
        url = item.get("url", "").strip()

        if not content:
            continue

        # Remove duplicate URLs
        if url:
            if url in seen_urls:
                continue
            seen_urls.add(url)

        # Ignore extremely short content
        if len(content) < 80:
            continue

        cleaned.append(item)

    return cleaned


# ============================================================
# One Query (Sequential Execution)
# ============================================================

def research_one_query(query: str) -> list[dict]:
    results = []

    # 1. Tavily
    tavily_results = search_tavily(query, max_results=3)
    results.extend(tavily_results)

    # 2. Wikipedia
    # wikipedia_results = search_wikipedia(query, max_results=1)
    # results.extend(wikipedia_results)
    # 3. DuckDuckGo
    duckduckgo_results = search_duckduckgo(query, max_results=1)
    results.extend(duckduckgo_results)

    # 4. ArXiv
        # arxiv_results = search_arxiv(query, max_results=1)
        # results.extend(arxiv_results)

    # Attach search query tag
    for item in results:
        item["query"] = query

    # Filter out empty or duplicate entries
    return clean_evidence(results)


# ============================================================
# Main Research Tool (Sequential Loop over Queries)
# ============================================================


def execute_research_tools(queries: list[str], max_workers: int = 4) -> list[dict]:
    all_results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(research_one_query, q): q for q in queries}
        for future in as_completed(futures):
            query = futures[future]
            try:
                results = future.result()
                print(f"🔎 {query} → {len(results)} clean results")
                all_results.extend(results)
            except Exception as e:
                print(f"Error researching query '{query}': {e}")

    return clean_evidence(all_results)