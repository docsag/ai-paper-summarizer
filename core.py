import sys
import os
import requests
import json
from datetime import datetime

# Ensure local modules are importable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

summarize_path = os.path.abspath(os.path.join(current_dir, "summarize"))
if summarize_path not in sys.path:
    sys.path.append(summarize_path)

from search.semantic_scholar import search_papers
from fetch.unpaywall import get_open_access_pdf
from parse.pdf_parser import extract_sections_from_pdf
from summarize.summarizer import summarize_section
from storage.db import insert_summary

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SEMANTIC_SCHOLAR_LOOKUP = "https://api.semanticscholar.org/graph/v1/paper/"

def download_pdf(pdf_url, save_path):
    try:
        print(f"⬇ Downloading PDF from: {pdf_url}")
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        print(f"❌ Failed to download PDF: {e}")
        return False

def fetch_metadata_from_semantic_scholar(doi):
    url = SEMANTIC_SCHOLAR_LOOKUP + doi
    params = {"fields": "title,year,journal,authors"}
    try:
        print(f"🔍 Fetching metadata for DOI: {doi}")
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
        print(f"❌ Metadata fetch error: {e}")
        return {}

def summarize_paper_from_doi(doi):
    print(f"\n📥 Processing DOI: {doi}")
    oa_info = get_open_access_pdf(doi)
    if not oa_info or not oa_info.get("pdf_url"):
        print("❌ No open access PDF found.")
        return

    pdf_url = oa_info["pdf_url"]
    pdf_path = os.path.join(OUTPUT_DIR, f"temp_{doi.replace('/', '_')}.pdf")
    if not download_pdf(pdf_url, pdf_path):
        return

    print("📄 Extracting sections from PDF...")
    sections = extract_sections_from_pdf(pdf_path)
    os.remove(pdf_path)

    summaries = {}
    for name, text in sections.items():
        if text.strip():
            print(f"🧠 Summarizing section: {name}")
            try:
                summary = summarize_section(name, text)
                summaries[name] = summary
                print(f"✅ Done: {name} ({len(summary)} chars)")
            except Exception as e:
                print(f"⚠️ Error summarizing {name}: {e}")

    if not summaries:
        print("⚠️ No valid summaries generated. Skipping DB insert.")
        return

    metadata = fetch_metadata_from_semantic_scholar(doi)
    metadata["doi"] = doi
    metadata["summarized_at"] = datetime.utcnow().isoformat()
    metadata["summaries"] = summaries

    print("📦 Saving metadata to DB...")
    try:
        insert_summary(metadata)
        print("✅ Successfully inserted summary into database.")
    except Exception as e:
        print(f"❌ DB insert failed: {e}")
        return

    # Save local copies (optional)
    txt_path = os.path.join(OUTPUT_DIR, f"{doi.replace('/', '_')}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"DOI: {doi}\n")
        for field in ("title", "year", "journal"):
            f.write(f"{field.title()}: {metadata.get(field, 'N/A')}\n")
        for section, summary in summaries.items():
            f.write(f"\n--- {section.upper()} ---\n{summary}\n")

    json_path = os.path.join(OUTPUT_DIR, f"{doi.replace('/', '_')}.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(metadata, jf, indent=2)

    print(f"📁 Summary saved to:\n- {txt_path}\n- {json_path}")

def summarize_multiple_papers(dois):
    for doi in dois:
        summarize_paper_from_doi(doi)

if __name__ == "__main__":
    test_dois = [
        "10.1038/s41586-020-2649-2",
        "10.1126/science.abd4570"
    ]
    summarize_multiple_papers(test_dois)