import requests
from utils.logger import get_logger

log = get_logger("greenhouse")


class GreenhouseScraper:
    def extract(self, company_slug):
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                log.error(f"Greenhouse {company_slug}: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": company_slug,
                    "location": j.get("location", {}).get("name", ""),
                    "url": j.get("absolute_url", ""),
                    "description": j.get("content", ""),
                    "source": "greenhouse",
                })
            return jobs
        except Exception as e:
            log.error(f"Greenhouse {company_slug} failed: {e}")
            return []
