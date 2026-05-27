# post_results.py
import json
import time
from pathlib import Path

from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, SCORE_THRESHOLD_FULL, SCORE_THRESHOLD_MENTION
from renderer.pdf_builder import render_cover_letter_pdf
from poster.discord_poster import DiscordPoster
from utils.logger import get_logger

log = get_logger("post_results")

DATA_DIR = Path("data")
PDF_DIR = DATA_DIR / "pdfs"


def run():
    scored_path = DATA_DIR / "scored_jobs.json"
    if not scored_path.exists():
        log.error("No scored_jobs.json found")
        return

    with open(scored_path) as f:
        data = json.load(f)

    jobs = data.get("jobs", [])
    if not jobs:
        log.info("No jobs in scored_jobs.json")
        return

    PDF_DIR.mkdir(parents=True, exist_ok=True)

    poster = DiscordPoster(bot_token=DISCORD_BOT_TOKEN, channel_id=DISCORD_CHANNEL_ID)

    top_jobs = [j for j in jobs if j.get("score", 0) >= SCORE_THRESHOLD_FULL]
    mention_jobs = [j for j in jobs if SCORE_THRESHOLD_MENTION <= j.get("score", 0) < SCORE_THRESHOLD_FULL]

    scrape_data = {}
    for fname in ["filtered_jobs.json", "scraped_jobs.json"]:
        spath = DATA_DIR / fname
        if spath.exists():
            with open(spath) as f:
                scrape_data = json.load(f)
            break

    poster.post_summary(
        total_scraped=scrape_data.get("total_scraped", 0),
        unique=scrape_data.get("unique_jobs", 0),
        top_matches=len(top_jobs),
        worth_a_look=len(mention_jobs),
        errors=scrape_data.get("errors", []),
        elapsed=scrape_data.get("elapsed_seconds", 0),
    )
    time.sleep(1)

    if not top_jobs and not mention_jobs:
        near_miss = jobs[0] if jobs else None
        poster.post_no_matches(
            total_scanned=scrape_data.get("unique_jobs", 0),
            near_miss=near_miss,
        )
        return

    for job in top_jobs[:20]:
        cover_pdf = None
        safe_name = f"{job['company']}_{job['title']}".replace(" ", "_").replace("/", "-")[:50]

        if job.get("cover_letter"):
            cover_pdf = str(PDF_DIR / f"cover_{safe_name}.pdf")
            render_cover_letter_pdf(job["cover_letter"], cover_pdf)

        poster.post_job(job, cover_letter_pdf=cover_pdf)
        time.sleep(1.5)

    if mention_jobs:
        poster.post_compact_list(mention_jobs[:12])

    log.info(f"Posted {len(top_jobs)} top jobs + {len(mention_jobs)} mentions to Discord")


if __name__ == "__main__":
    run()
