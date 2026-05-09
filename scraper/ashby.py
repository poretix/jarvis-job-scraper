import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("ashby")


class AshbyScraper:
    def extract(self, company_slug):
        url = "https://api.ashbyhq.com/posting-api/job-board/" + company_slug
        try:
            resp = requests.post(url, json={}, timeout=30)
            if resp.status_code != 200:
                log.error(f"Ashby {company_slug}: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for j in data.get("jobs", []):
                desc_html = j.get("descriptionHtml", "")
                desc_text = BeautifulSoup(desc_html, "html.parser").get_text(separator=" ") if desc_html else ""
                jobs.append({
                    "title": j.get("title", ""),
                    "company": company_slug,
                    "location": j.get("location", ""),
                    "url": j.get("jobUrl", ""),
                    "description": desc_text,
                    "source": "ashby",
                })
            return jobs
        except Exception as e:
            log.error(f"Ashby {company_slug} failed: {e}")
            return []
