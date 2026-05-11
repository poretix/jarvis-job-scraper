import json
import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("yc_startup")

ROLE_PATHS = [
    "/jobs/l/product-manager",
    "/jobs/l/operations",
    "/jobs/l/marketing",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}


class YCStartupScraper:
    BASE_URL = "https://www.workatastartup.com"

    def extract(self, role_query=None):
        all_jobs = []
        seen_ids = set()

        for path in ROLE_PATHS:
            try:
                resp = requests.get(
                    f"{self.BASE_URL}{path}",
                    headers=HEADERS,
                    timeout=30,
                )
                if resp.status_code != 200:
                    log.error(f"YC {path}: HTTP {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                el = soup.find(attrs={"data-page": True})
                if not el:
                    continue

                data = json.loads(el["data-page"])
                jobs_data = data.get("props", {}).get("jobs", [])

                for j in jobs_data:
                    jid = j.get("id")
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    batch = j.get("companyBatch", "")
                    company = j.get("companyName", "")
                    if batch:
                        company = f"{company} ({batch})"

                    all_jobs.append({
                        "title": j.get("title", ""),
                        "company": company,
                        "location": j.get("location", ""),
                        "url": j.get("applyUrl", f"{self.BASE_URL}/jobs/{jid}"),
                        "description": j.get("companyOneLiner", ""),
                        "source": "yc_startup",
                    })

            except Exception as e:
                log.error(f"YC {path} failed: {e}")

        log.info(f"YC Work at a Startup: {len(all_jobs)} jobs")
        return all_jobs
