
import requests

UNPAYWALL_API = "https://api.unpaywall.org/v2/"
CONTACT_EMAIL = "your@email.com"  # Replace with your email (required by Unpaywall)

def get_open_access_pdf(doi):
    url = f"{UNPAYWALL_API}{doi}"
    params = {"email": CONTACT_EMAIL}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("is_oa") and data.get("best_oa_location"):
            return {
                "title": data.get("title"),
                "pdf_url": data["best_oa_location"].get("url_for_pdf"),
                "source": data["best_oa_location"].get("host_type"),
                "oa_status": data.get("oa_status")
            }
        else:
            return None
    except requests.RequestException as e:
        print(f"Unpaywall API error: {e}")
        return None
