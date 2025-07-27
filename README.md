# AI Paper Summarizer

An AI-powered app to:
- Search for open-access scientific papers by DOI or keyword
- Automatically download and parse PDFs
- Summarize sections in layperson-friendly language
- Browse and filter summaries via a Streamlit UI
- Store all results in a local SQLite database

## 🚀 Features
- DOI & PDF input support
- Section-wise summarization using GPT-4
- Metadata enrichment from Semantic Scholar
- SQLite-based caching and filtering
- Streamlit-based web UI with search & download

## 🛠 Installation

```bash
git clone https://github.com/yourusername/ai-paper-summarizer.git
cd ai-paper-summarizer
pip install -r requirements.txt
```

## 🔑 Setup

Set your OpenAI key (e.g., in `.env` or Streamlit secrets):

```bash
export OPENAI_API_KEY=your-key
```

## ▶️ Run the App

```bash
streamlit run app/main.py
```

## 📦 File Structure

```
app/                # Streamlit UI
fetch/              # PDF & metadata download
search/             # Semantic Scholar integration
summarize/          # GPT-4 summarization logic
storage/            # SQLite database
parse/              # PDF section extractor
main.py             # CLI processor for DOIs
output/             # JSON, TXT, and SQLite outputs
```
