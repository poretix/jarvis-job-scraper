import re
import requests
from utils.logger import get_logger

log = get_logger("hn_hiring")

HN_API = "https://hacker-news.firebaseio.com/v0"


class HNHiringScraper:
    def extract(self, story_id=None):
        try:
            if not story_id:
                story_id = self._find_latest_hiring_thread()
                if not story_id:
                    log.warning("No HN hiring thread found")
                    return []

            resp = requests.get(f"{HN_API}/item/{story_id}.json", timeout=10)
            if resp.status_code != 200:
                return []
            story = resp.json()
            comment_ids = story.get("kids", [])[:100]

            jobs = []
            for cid in comment_ids:
                try:
                    cr = requests.get(f"{HN_API}/item/{cid}.json", timeout=5)
                    if cr.status_code != 200:
                        continue
                    comment = cr.json()
                    if comment.get("dead") or comment.get("deleted"):
                        continue
                    text = comment.get("text", "")
                    parsed = self._parse_comment(text, cid)
                    if parsed:
                        jobs.append(parsed)
                except Exception:
                    continue
            return jobs

        except Exception as e:
            log.error(f"HN hiring failed: {e}")
            return []

    def _find_latest_hiring_thread(self):
        try:
            resp = requests.get(f"{HN_API}/user/whoishiring.json", timeout=10)
            if resp.status_code != 200:
                return None
            submitted = resp.json().get("submitted", [])
            for sid in submitted[:5]:
                sr = requests.get(f"{HN_API}/item/{sid}.json", timeout=5)
                if sr.status_code == 200:
                    item = sr.json()
                    title = item.get("title", "")
                    if "Who is hiring" in title:
                        return sid
        except Exception:
            pass
        return None

    def _parse_comment(self, text, comment_id):
        clean = re.sub(r"<[^>]+>", "\n", text).strip()
        parts = clean.split("|")
        company = parts[0].strip() if parts else "Unknown"
        title = parts[1].strip() if len(parts) > 1 else ""
        location = parts[2].strip() if len(parts) > 2 else ""

        url_match = re.search(r"https?://[^\s<\"]+", text)
        url = url_match.group(0) if url_match else f"https://news.ycombinator.com/item?id={comment_id}"

        return {
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "description": clean,
            "source": "hn_hiring",
        }
