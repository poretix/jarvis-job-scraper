import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("startups_gallery")


class StartupsGalleryScraper:
    BASE_URL = "https://startups.gallery"

    def extract(self):
        try:
            resp = requests.get(
                f"{self.BASE_URL}/jobs",
                headers={"User-Agent": "Jarvis/1.0"},
                timeout=30,
            )
            if resp.status_code != 200:
                log.error(f"startups.gallery: HTTP {resp.status_code}")
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = []

            # Selectors are approximate — verify against live site and adjust
            for card in soup.select("[class*='job'], [class*='listing'], [class*='card']"):
                title_el = card.select_one("a[class*='title'], h3, h4")
                company_el = card.select_one("[class*='company']")
                location_el = card.select_one("[class*='location']")
                if not title_el:
                    continue
                href = title_el.get("href", "")
                url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                jobs.append({
                    "title": title_el.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "url": url,
                    "description": "",
                    "source": "startups_gallery",
                })
            return jobs

        except Exception as e:
            log.error(f"startups.gallery failed: {e}")
            return []
