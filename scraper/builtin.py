import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("builtin")

BUILTIN_URLS = {
    "sf": "https://www.builtinsf.com/jobs",
    "nyc": "https://www.builtinnyc.com/jobs",
}


class BuiltInScraper:
    def extract(self):
        all_jobs = []
        for city, base_url in BUILTIN_URLS.items():
            try:
                resp = requests.get(
                    base_url,
                    params={"category": "product-management"},
                    headers={"User-Agent": "Jarvis/1.0"},
                    timeout=30,
                )
                if resp.status_code != 200:
                    log.error(f"BuiltIn {city}: HTTP {resp.status_code}")
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("[data-id='job-card']")
                for card in cards:
                    title_el = card.select_one("h2 a")
                    company_el = card.select_one("[data-id='company-title']")
                    if not title_el:
                        continue
                    href = title_el.get("href", "")
                    url = href if href.startswith("http") else f"https://www.builtin{city}.com{href}"
                    all_jobs.append({
                        "title": title_el.get_text(strip=True),
                        "company": company_el.get_text(strip=True) if company_el else "",
                        "location": city.upper(),
                        "url": url,
                        "description": "",
                        "source": "builtin",
                    })
            except Exception as e:
                log.error(f"BuiltIn {city} failed: {e}")
        return all_jobs
