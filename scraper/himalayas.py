import requests
from utils.logger import get_logger

log = get_logger("himalayas")


class HimalayasScraper:
    URL = "https://himalayas.app/jobs/api"

    def extract(self):
        try:
            resp = requests.get(
                self.URL,
                params={"limit": 50},
                headers={"User-Agent": "Jarvis/1.0"},
                timeout=30,
            )
            if resp.status_code != 200:
                log.error(f"Himalayas: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for item in data.get("jobs", []):
                jobs.append({
                    "title": item.get("title", ""),
                    "company": item.get("companyName", ""),
                    "location": ", ".join(item.get("locationRestrictions", [])) or "Remote",
                    "url": item.get("applicationLink", "") or f"https://himalayas.app/jobs/{item.get('slug', '')}",
                    "description": item.get("description", ""),
                    "source": "himalayas",
                })
            return jobs
        except Exception as e:
            log.error(f"Himalayas failed: {e}")
            return []
