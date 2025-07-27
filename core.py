import sys
import os

# Ensure the root directory (where core.py is) is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    # Explicitly add 'summarize' to path in case it's not found
summarize_path = os.path.abspath(os.path.join(current_dir, "summarize"))
if summarize_path not in sys.path:
    sys.path.append(summarize_path)
from search.semantic_scholar import search_papers
from fetch.unpaywall import get_open_access_pdf
from parse.pdf_parser import extract_sections_from_pdf
from summarize.summarizer import summarize_section
from storage.db import insert_summary
import os
import requests
import json
from datetime import datetime

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SEMANTIC_SCHOLAR_LOOKUP = "https://api.semanticscholar.org/graph/v1/paper/"

def download_pdf(pdf_url, save_path):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        print(f"Failed to download PDF: {e}")
        return False

def fetch_metadata_from_semantic_scholar(doi):
    url = SEMANTIC_SCHOLAR_LOOKUP + doi
    params = {
        "fields": "title,year,journal,authors"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "title": data.get("title"),
            "year": data.get("year"),
            "journal": data.get("journal", {}).get("name"),
            "authors": [a.get("name") for a in data.get("authors", [])]
        }
    except requests.RequestException as e:
        print(f"Metadata fetch error: {e}")
        return {}

def summarize_paper_from_doi(doi):
    print(f"\n📥 Processing DOI: {doi}")
    oa_info = get_open_access_pdf(doi)
    if not oa_info or not oa_info.get("pdf_url"):
        print("❌ No open access PDF found.")
        return

    pdf_url = oa_info["pdf_url"]
    pdf_path = f"temp_{doi.replace('/', '_')}.pdf"
    if not download_pdf(pdf_url, pdf_path):
        print("❌ Failed to download PDF.")
        return

    print("✅ PDF downloaded. Extracting sections...")
    sections = extract_sections_from_pdf(pdf_path)
    os.remove(pdf_path)

    summaries = {}
    print(f"📄 Found {len(sections)} sections. Summarizing...")
    for name, text in sections.items():
        if text.strip():
            summary = summarize_section(name, text)
            summaries[name] = summary
            print(f"📝 Summary for '{name}': {summary[:100]}...")

    metadata = fetch_metadata_from_semantic_scholar(doi)
    metadata["doi"] = doi
    metadata["summarized_at"] = datetime.utcnow().isoformat()
    metadata["summaries"] = summaries

    print("📦 Metadata ready:")
    print(json.dumps(metadata, indent=2))

    print("📥 Inserting into DB...")
    insert_summary(metadata)
    print("✅ Summary inserted into database!")

    # Optional local write
    txt_filename = os.path.join(OUTPUT_DIR, f"{doi.replace('/', '_')}.txt")
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(f"DOI: {doi}\n")
        for k in ("title", "year", "journal"):
            if metadata.get(k):
                f.write(f"{k.capitalize()}: {metadata[k]}\n")
        f.write("\n")
        for name, summary in summaries.items():
            f.write(f"--- {name.upper()} ---\n{summary}\n\n")

    json_filename = os.path.join(OUTPUT_DIR, f"{doi.replace('/', '_')}.json")
    with open(json_filename, "w", encoding="utf-8") as jf:
        json.dump(metadata, jf, indent=2)