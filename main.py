# main.py
import json
import time
from pathlib import Path

from config import (
    BRAVE_API_KEY,
    BRAVE_SEARCH_QUERIES,
    BRAVE_LINKEDIN_QUERIES,
    DREAMWORK_API_KEY,
    ROLE_TITLES,
    title_matches_target,
)
from scraper.brave_search import BraveSearchScraper
from scraper.greenhouse import GreenhouseScraper
from scraper.lever import LeverScraper
from scraper.ashby import AshbyScraper
from scraper.remoteok import RemoteOKScraper
from scraper.himalayas import HimalayasScraper
from scraper.builtin import BuiltInScraper
from scraper.hn_hiring import HNHiringScraper
from scraper.yc_startup import YCStartupScraper
from scraper.startups_gallery import StartupsGalleryScraper
from scraper.dreamwork import DreamworkScraper
from utils.deduper import Deduper
from utils.logger import get_logger

log = get_logger("main")
DATA_DIR = Path("data")


def run_discovery():
    """Use Brave Search to discover ATS board URLs."""
    if not BRAVE_API_KEY:
        log.warning("No BRAVE_API_KEY — skipping discovery")
        return [], []

    brave = BraveSearchScraper(api_key=BRAVE_API_KEY)
    discovered = []

    all_titles = []
    for titles in ROLE_TITLES.values():
        all_titles.extend(titles[:3])  # top 3 per category to stay under query budget

    for title in all_titles[:15]:  # cap at 15 queries per run
        for query_template in BRAVE_SEARCH_QUERIES[:2]:  # 2 templates per title
            query = query_template.format(title=title)
            results = brave.discover(query)
            discovered.extend(results)
            time.sleep(0.5)

    log.info(f"Discovery found {len(discovered)} ATS URLs")

    # LinkedIn discovery via Brave snippets
    linkedin_jobs = []
    linkedin_titles = ["Product Manager", "Growth Manager", "Chief of Staff",
                       "Strategy Operations", "Business Operations"]
    for title in linkedin_titles:
        for query_template in BRAVE_LINKEDIN_QUERIES:
            query = query_template.format(title=title)
            jobs = brave.discover_linkedin(query)
            linkedin_jobs.extend(jobs)
            time.sleep(0.5)

    log.info(f"LinkedIn via Brave: {len(linkedin_jobs)} jobs")
    return discovered, linkedin_jobs


def run_extraction(discovered_urls):
    """Extract jobs from all sources."""
    all_jobs = []
    errors = []

    # Extract from discovered ATS boards
    greenhouse_slugs = set()
    lever_slugs = set()
    ashby_slugs = set()
    for item in discovered_urls:
        url = item["url"]
        if item["source"] == "greenhouse":
            slug = url.split("boards.greenhouse.io/")[1].split("/")[0]
            greenhouse_slugs.add(slug)
        elif item["source"] == "lever":
            slug = url.split("jobs.lever.co/")[1].split("/")[0]
            lever_slugs.add(slug)
        elif item["source"] == "ashby":
            slug = url.split("jobs.ashbyhq.com/")[1].split("/")[0]
            ashby_slugs.add(slug)

    gh = GreenhouseScraper()
    for slug in greenhouse_slugs:
        try:
            all_jobs.extend(gh.extract(slug))
        except Exception as e:
            errors.append(f"greenhouse/{slug}: {e}")

    lv = LeverScraper()
    for slug in lever_slugs:
        try:
            all_jobs.extend(lv.extract(slug))
        except Exception as e:
            errors.append(f"lever/{slug}: {e}")

    ab = AshbyScraper()
    for slug in ashby_slugs:
        try:
            all_jobs.extend(ab.extract(slug))
        except Exception as e:
            errors.append(f"ashby/{slug}: {e}")

    # Public API sources
    source_runners = [
        ("remoteok", lambda: RemoteOKScraper().extract()),
        ("himalayas", lambda: HimalayasScraper().extract()),
        ("builtin", lambda: BuiltInScraper().extract()),
        ("hn_hiring", lambda: HNHiringScraper().extract()),
        ("yc_startup", lambda: YCStartupScraper().extract()),
        ("startups_gallery", lambda: StartupsGalleryScraper().extract()),
    ]

    if DREAMWORK_API_KEY:
        source_runners.append(
            ("dreamwork", lambda: DreamworkScraper(DREAMWORK_API_KEY).extract())
        )

    for name, runner in source_runners:
        try:
            jobs = runner()
            all_jobs.extend(jobs)
            log.info(f"{name}: {len(jobs)} jobs")
        except Exception as e:
            errors.append(f"{name}: {e}")
            log.error(f"{name} failed: {e}")

    pre_filter = len(all_jobs)
    all_jobs = [j for j in all_jobs if title_matches_target(j.get("title", ""))]
    log.info(f"Title filter: {pre_filter} → {len(all_jobs)} relevant jobs")

    return all_jobs, errors


def run_scrape():
    """Full scrape pipeline: discover → extract → deduplicate → save."""
    DATA_DIR.mkdir(exist_ok=True)

    start = time.time()
    discovered, linkedin_jobs = run_discovery()
    all_jobs, errors = run_extraction(discovered)
    all_jobs.extend(linkedin_jobs)

    deduper = Deduper()
    unique_jobs = deduper.deduplicate(all_jobs)

    elapsed = time.time() - start
    log.info(f"Scraped {len(all_jobs)} → {len(unique_jobs)} unique jobs in {elapsed:.1f}s")

    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_scraped": len(all_jobs),
        "unique_jobs": len(unique_jobs),
        "errors": errors,
        "elapsed_seconds": round(elapsed, 1),
        "jobs": unique_jobs,
    }

    output_path = DATA_DIR / "scraped_jobs.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    log.info(f"Saved to {output_path}")
    return output


if __name__ == "__main__":
    run_scrape()
