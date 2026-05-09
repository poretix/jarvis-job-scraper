class Deduper:
    def deduplicate(self, jobs):
        seen = set()
        unique = []
        for job in jobs:
            url = job["url"].rstrip("/")
            if url not in seen:
                seen.add(url)
                unique.append(job)
        return unique
