import re
import requests
from utils.logger import get_logger

log = get_logger("brave_search")

ATS_PATTERNS = {
    "greenhouse": "boards.greenhouse.io",
    "lever": "jobs.lever.co",
    "ashby": "jobs.ashbyhq.com",
}

LINKEDIN_JOB_PATTERN = re.compile(r"linkedin\.com/jobs/view/")


class BraveSearchScraper:
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key):
        self.api_key = api_key

    def _search(self, query, count=20):
        resp = requests.get(
            self.BASE_URL,
            headers={"X-Subscription-Token": self.api_key, "Accept": "application/json"},
            params={"q": query, "count": count},
            timeout=10,
        )
        if resp.status_code != 200:
            log.error(f"Brave API returned {resp.status_code}: {resp.text[:200]}")
            return []
        return resp.json().get("web", {}).get("results", [])

    def discover(self, query, count=20):
        try:
            results = self._search(query, count)
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

    def discover_linkedin(self, query, count=10):
        try:
            results = self._search(query, count)
            jobs = []
            for r in results:
                url = r.get("url", "")
                if not LINKEDIN_JOB_PATTERN.search(url):
                    continue

                snippet_title = r.get("title", "")
                description = r.get("description", "")

                title, company = self._parse_linkedin_title(snippet_title)
                if not title:
                    continue

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": "",
                    "url": url,
                    "description": description,
                    "source": "linkedin_via_brave",
                })
            return jobs

        except Exception as e:
            log.error(f"Brave LinkedIn search failed: {e}")
            return []

    def _parse_linkedin_title(self, snippet_title):
        snippet_title = snippet_title.replace(" | LinkedIn", "").strip()

        patterns = [
            r"^(.+?)\s+hiring\s+(.+?)(?:\s+in\s+.+)?$",
            r"^(.+?)\s*[-–—]\s*(.+)$",
        ]

        for pattern in patterns:
            match = re.match(pattern, snippet_title)
            if match:
                part_a, part_b = match.group(1).strip(), match.group(2).strip()
                if "hiring" in snippet_title.lower():
                    return part_b, part_a
                return part_a, part_b

        return snippet_title, ""

    def _classify_source(self, url):
        for source, pattern in ATS_PATTERNS.items():
            if pattern in url:
                return source
        return None
