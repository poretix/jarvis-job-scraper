import requests
from utils.logger import get_logger

log = get_logger("brave_search")

ATS_PATTERNS = {
    "greenhouse": "boards.greenhouse.io",
    "lever": "jobs.lever.co",
    "ashby": "jobs.ashbyhq.com",
}


class BraveSearchScraper:
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key):
        self.api_key = api_key

    def discover(self, query, count=20):
        try:
            resp = requests.get(
                self.BASE_URL,
                headers={"X-Subscription-Token": self.api_key, "Accept": "application/json"},
                params={"q": query, "count": count},
                timeout=10,
            )
            if resp.status_code != 200:
                log.error(f"Brave API returned {resp.status_code}: {resp.text[:200]}")
                return []

            results = resp.json().get("web", {}).get("results", [])
            discovered = []
            for r in results:
                url = r.get("url", "")
                title = r.get("title", "")
                source = self._classify_source(url)
                if source:
                    discovered.append({"url": url, "title": title, "source": source})
            return discovered

        except Exception as e:
            log.error(f"Brave search failed: {e}")
            return []

    def _classify_source(self, url):
        for source, pattern in ATS_PATTERNS.items():
            if pattern in url:
                return source
        return None
