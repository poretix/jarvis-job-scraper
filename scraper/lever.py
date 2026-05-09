import requests
from utils.logger import get_logger

log = get_logger("lever")


class LeverScraper:
    def extract(self, company_slug):
        url = f"https://api.lever.co/v0/postings/{company_slug}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                log.error(f"Lever {company_slug}: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for j in data:
                jobs.append({
                    "title": j.get("text", ""),
                    "company": company_slug,
                    "location": j.get("categories", {}).get("location", ""),
                    "url": j.get("hostedUrl", ""),
                    "description": j.get("descriptionPlain", ""),
                    "source": "lever",
                })
            return jobs
        except Exception as e:
            log.error(f"Lever {company_slug} failed: {e}")
            return []
