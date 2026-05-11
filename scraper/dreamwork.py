import requests
from utils.logger import get_logger

log = get_logger("dreamwork")

BASE_URL = "https://api-gateway-production-e591.up.railway.app/api"

SEARCH_QUERIES = [
    {"query": "Growth Manager startup", "functions": ["Product"], "seniorities": ["MID", "SENIOR"]},
    {"query": "Product Manager startup", "functions": ["Product"], "seniorities": ["JUNIOR", "MID", "SENIOR"]},
    {"query": "Strategy Operations startup", "functions": ["Product"], "seniorities": ["MID", "SENIOR"]},
    {"query": "Chief of Staff startup", "functions": ["Product"], "seniorities": ["MID", "SENIOR"]},
    {"query": "Business Operations startup", "functions": ["Product"], "seniorities": ["MID", "SENIOR"]},
]

LOCATIONS = ["San Francisco", "New York", "Remote"]


class DreamworkScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def extract(self):
        all_jobs = []
        seen_ids = set()

        for search in SEARCH_QUERIES:
            try:
                payload = {
                    "query": search["query"],
                    "functions": search.get("functions", []),
                    "seniorities": search.get("seniorities", []),
                    "locations": LOCATIONS,
                    "postedWithin": "14d",
                    "sort": "recent",
                    "limit": 50,
                }

                resp = requests.post(
                    f"{BASE_URL}/v2/jobs/search",
                    headers=self.headers,
                    json=payload,
                    timeout=15,
                )

                if resp.status_code != 200:
                    log.error(f"Dreamwork search failed: {resp.status_code} {resp.text[:200]}")
                    continue

                data = resp.json()
                results = data.get("results", data.get("jobs", []))

                for job in results:
                    jid = job.get("id") or job.get("jobId", "")
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    all_jobs.append({
                        "title": job.get("title", ""),
                        "company": job.get("company", job.get("companyName", "")),
                        "location": job.get("location", ""),
                        "url": job.get("webUrl", job.get("url", "")),
                        "description": job.get("description", "")[:500],
                        "source": "dreamwork",
                    })

            except Exception as e:
                log.error(f"Dreamwork query '{search['query']}' failed: {e}")

        log.info(f"Dreamwork: {len(all_jobs)} jobs")
        return all_jobs
