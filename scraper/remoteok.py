import requests
from utils.logger import get_logger

log = get_logger("remoteok")


class RemoteOKScraper:
    URL = "https://remoteok.com/api"

    def extract(self):
        try:
            resp = requests.get(self.URL, headers={"User-Agent": "Jarvis/1.0"}, timeout=30)
            if resp.status_code != 200:
                log.error(f"RemoteOK: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for item in data[1:]:  # first element is metadata
                jobs.append({
                    "title": item.get("position", ""),
                    "company": item.get("company", ""),
                    "location": item.get("location", "Remote"),
                    "url": item.get("url", f"https://remoteok.com/jobs/{item.get('id', '')}"),
                    "description": item.get("description", ""),
                    "source": "remoteok",
                })
            return jobs
        except Exception as e:
            log.error(f"RemoteOK failed: {e}")
            return []
