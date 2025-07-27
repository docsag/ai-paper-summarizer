
import fitz  # PyMuPDF
import re

def extract_sections_from_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    sections = {
        "abstract": extract_section(full_text, r"(?i)abstract"),
        "introduction": extract_section(full_text, r"(?i)introduction"),
        "methods": extract_section(full_text, r"(?i)(methods|methodology|materials and methods)"),
        "results": extract_section(full_text, r"(?i)results"),
        "discussion": extract_section(full_text, r"(?i)(discussion|conclusion|summary)")
    }
    return sections

def extract_section(text, section_heading_regex):
    pattern = rf"{section_heading_regex}.*?(?=\n[A-Z][A-Za-z\s]{2,30}\n)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(0).strip()
    return ""
