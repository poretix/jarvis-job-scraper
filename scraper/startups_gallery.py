import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("startups_gallery")

ATS_DOMAINS = ["greenhouse.io", "lever.co", "ashbyhq.com"]


class StartupsGalleryScraper:
    BASE_URL = "https://startups.gallery"

    def extract(self):
        try:
            resp = requests.get(
                f"{self.BASE_URL}/jobs",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
                timeout=30,
            )
            if resp.status_code != 200:
                log.error(f"startups.gallery: HTTP {resp.status_code}")
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = []

            for link in soup.find_all("a", href=True):
                href = link["href"]
                if not any(domain in href for domain in ATS_DOMAINS):
                    continue

                title_el = link.find("h2")
                info_el = link.find("p")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                company = ""
                location = ""
                if info_el:
                    parts = info_el.get_text(strip=True).split("·")
                    if len(parts) >= 1:
                        company = parts[0].strip()
                    if len(parts) >= 2:
                        location = parts[1].strip()

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": href,
                    "description": "",
                    "source": "startups_gallery",
                })

            log.info(f"startups.gallery: {len(jobs)} jobs")
            return jobs

        except Exception as e:
            log.error(f"startups.gallery failed: {e}")
            return []
