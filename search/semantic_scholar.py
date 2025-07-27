
import requests

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"

def search_papers(query, limit=5):
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,doi,openAccessPdf,abstract"
    }
    try:
        response = requests.get(SEMANTIC_SCHOLAR_API, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for paper in data.get("data", []):
            results.append({
                "title": paper.get("title"),
                "authors": [a.get("name") for a in paper.get("authors", [])],
                "year": paper.get("year"),
                "doi": paper.get("doi"),
                "abstract": paper.get("abstract"),
                "pdf_url": paper.get("openAccessPdf", {}).get("url")
            })
        return results
    except requests.RequestException as e:
        print(f"Semantic Scholar API error: {e}")
        return []
