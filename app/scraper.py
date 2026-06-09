import os
import re
import time
import json
import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.config import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


BASE_URL = "https://intranet.canalcapital.gov.co/ccintnt/"
OUTPUT_FILE = os.path.join(settings.DATA_DIR, "intranet_scraping.json")

MAX_PAGES = 30
WAIT_SECONDS = 1


def is_internal_link(url: str) -> bool:
    parsed_base = urlparse(BASE_URL)
    parsed_url = urlparse(url)

    return parsed_url.netloc == parsed_base.netloc or parsed_url.netloc == ""


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "iframe", "svg"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return clean_text(text)


def get_links(html: str, current_url: str) -> list:
    soup = BeautifulSoup(html, "lxml")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(current_url, href)

        if is_internal_link(full_url):
            full_url = full_url.split("#")[0]
            links.append(full_url)

    return list(set(links))


def scrape_intranet():
    visited = set()
    pending = [BASE_URL]
    results = []

    headers = {
        "User-Agent": "CanalCapital-RAGBot/1.0"
    }

    while pending and len(visited) < MAX_PAGES:
        url = pending.pop(0)

        if url in visited:
            continue

        try:
            print(f"Scrapeando: {url}")

            response = requests.get(url, headers=headers, timeout=20, verify=False)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")

            if "text/html" not in content_type:
                continue

            html = response.text
            text = extract_text_from_html(html)

            if len(text) > 100:
                results.append({
                    "source": url,
                    "page": 1,
                    "text": text
                })

            visited.add(url)

            new_links = get_links(html, url)

            for link in new_links:
                if link not in visited and link not in pending:
                    pending.append(link)

            time.sleep(WAIT_SECONDS)

        except Exception as e:
            print(f"Error en {url}: {e}")

    os.makedirs(settings.DATA_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nScraping finalizado.")
    print(f"Páginas procesadas: {len(results)}")
    print(f"Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_intranet()