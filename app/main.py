
import streamlit as st
import sqlite3
import os
import json
from pathlib import Path
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import summarize_paper_from_doi
from parse.pdf_parser import extract_sections_from_pdf
from summarize.summarizer import summarize_section

DB_PATH = Path("output/summaries.db")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="AI Paper Summarizer", layout="wide")
st.title("📄 AI Paper Summarizer")

# ---- Sidebar: Input Section ----
st.sidebar.header("🔍 Input Options")

# Option 1: Enter DOI
doi_input = st.sidebar.text_input("Enter DOI")
if st.sidebar.button("Summarize DOI") and doi_input:
    summarize_paper_from_doi(doi_input.strip())
    st.sidebar.success("Summary generated!")

# Option 2: Upload PDF
uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
if uploaded_pdf and st.sidebar.button("Summarize PDF"):
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_pdf.read())
        tmp_path = tmp_file.name

    sections = extract_sections_from_pdf(tmp_path)
    summaries = {name: summarize_section(name, text) for name, text in sections.items() if text.strip()}

    filename_base = os.path.splitext(uploaded_pdf.name)[0].replace('/', '_')
    txt_path = os.path.join(OUTPUT_DIR, f"{filename_base}.txt")
    with open(txt_path, "w", encoding="utf-8") as tf:
        for name, summary in summaries.items():
            tf.write(f"--- {name.upper()} ---\n{summary}\n\n")

    st.sidebar.success("Uploaded PDF summarized and saved! (not stored in DB)")

# ---- Load from SQLite ----
def query_summaries(search_query=None, year_filter=None, journal_filter=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT doi, title, year, journal, authors, summaries_json FROM summaries WHERE 1=1"
    params = []

    if year_filter and year_filter != "All":
        query += " AND year = ?"
        params.append(int(year_filter))
    if journal_filter and journal_filter != "All":
        query += " AND journal = ?"
        params.append(journal_filter)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        doi, title, year, journal, authors, summaries_json = row
        summaries = json.loads(summaries_json)
        if search_query:
            match = any(search_query.lower() in s.lower() for s in summaries.values())
            if not match:
                continue
        results.append({
            "doi": doi,
            "title": title,
            "year": year,
            "journal": journal,
            "authors": authors,
            "summaries": summaries
        })
    return results

# ---- Filters ----
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT year FROM summaries ORDER BY year DESC")
year_options = [str(row[0]) for row in cursor.fetchall() if row[0]]
cursor.execute("SELECT DISTINCT journal FROM summaries ORDER BY journal")
journal_options = [row[0] for row in cursor.fetchall() if row[0]]
conn.close()

year_filter = st.sidebar.selectbox("Filter by year", ["All"] + year_options)
journal_filter = st.sidebar.selectbox("Filter by journal", ["All"] + journal_options)
search_query = st.text_input("Enter keyword to search in summaries")

# ---- Display Results ----
results = query_summaries(search_query, year_filter, journal_filter)
if not results:
    st.info("No summaries found with current filters.")
else:
    selected_title = st.selectbox("Select a paper:", [r["title"] or r["doi"] for r in results])
    selected = next(r for r in results if (r["title"] or r["doi"]) == selected_title)

    st.markdown(f"### DOI: `{selected['doi']}`")
    st.markdown(f"**Title**: {selected.get('title', 'N/A')}")
    st.markdown(f"**Year**: {selected.get('year', 'N/A')} | **Journal**: {selected.get('journal', 'N/A')}")

    for section, summary in selected.get("summaries", {}).items():
        with st.expander(section.title()):
            st.write(summary)

    json_data = json.dumps(selected, indent=2)
    st.download_button("📁 Download Summary JSON", data=json_data, file_name=f"{selected['doi'].replace('/', '_')}.json")
