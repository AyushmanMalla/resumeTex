import requests
from bs4 import BeautifulSoup
import re

def generic_scraper(url: str) -> str:
    """
    Fallback scraper that extracts all readable text on the page.
    The result may contain extra content such as disclaimers or headers/footers.
    This allows downstream NLP models to extract relevant sections like the job description.
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch URL: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract all visible text from <div>, <section>, <article>, <main>, <p>, <li>, etc.
    elements = soup.find_all(["div", "section", "article", "main", "p", "li"])
    page_text = "\n".join([el.get_text(separator=" ", strip=True) for el in elements if el.get_text(strip=True)])

    return page_text

print(generic_scraper("https://blackrock.wd1.myworkdayjobs.com/en-US/BlackRock_Professional/job/SN6-Singapore---20-Anson-Road/Aladdin-Client-Experience--Associate_R252778"))