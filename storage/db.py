import sqlite3
from pathlib import Path
import json
import os  # ✅ Needed for creating directories

DB_PATH = Path(__file__).resolve().parent.parent / "output" / "summaries.db"

# ✅ Fix: Make sure output/ directory exists BEFORE using it
os.makedirs(DB_PATH.parent, exist_ok=True)

# ✅ Now open the DB safely
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS summaries (
    doi TEXT PRIMARY KEY,
    title TEXT,
    year INTEGER,
    journal TEXT,
    authors TEXT,
    summarized_at TEXT,
    summaries_json TEXT
)
""")
conn.commit()
conn.close()

def insert_summary(metadata):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO summaries (doi, title, year, journal, authors, summarized_at, summaries_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata.get("doi"),
            metadata.get("title"),
            metadata.get("year"),
            metadata.get("journal"),
            ", ".join(metadata.get("authors", [])),
            metadata.get("summarized_at"),
            json.dumps(metadata.get("summaries", {}))
        ))
        conn.commit()