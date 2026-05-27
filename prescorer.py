"""Pre-scorer: narrows ~1,400 scraped jobs to top 30 candidates using keyword/regex scoring."""

import json
import re
from pathlib import Path

from config import EXCLUDED_INDUSTRIES, title_matches_target

# --- Constants ---

DESC_TRUNCATE = 2000
DEFAULT_MAX = 30

# --- Location matching (+3, cap 3) ---

_LOC_PATTERN = re.compile(
    r"(san francisco|\bsf\b|new york|\bnyc\b|\bremote\b)", re.IGNORECASE
)

# --- Growth signal keywords (+1 each, cap 4) ---

_GROWTH_KEYWORDS = [
    r"growth", r"experimentation", r"acquisition", r"retention",
    r"\bplg\b", r"product[- ]led", r"\bgtm\b", r"conversion",
    r"funnel", r"metrics", r"a/b test", r"lifecycle",
    r"monetization", r"pricing", r"revenue", r"activation",
    r"referral", r"onboarding", r"churn", r"engagement",
    r"attribution", r"\bseo\b", r"\bcro\b", r"\bcac\b",
    r"customer acquisition cost", r"\bltv\b", r"lifetime value",
    r"north star metric", r"growth loop", r"growth loops",
    r"viral", r"virality", r"paywall", r"segmentation",
    r"cohort", r"\bdtc\b", r"direct to consumer", r"\bd2c\b",
]
_GROWTH_PATTERN = re.compile("|".join(_GROWTH_KEYWORDS), re.IGNORECASE)
_GROWTH_CAP = 4

# --- Product signal keywords (+1 each, cap 3) ---

_PRODUCT_KEYWORDS = [
    r"roadmap", r"user research", r"\bprd\b", r"product requirements",
    r"product specs", r"product strategy", r"cross[- ]functional",
    r"stakeholder", r"sprint", r"backlog", r"prioritization",
    r"feature prioritization", r"shipping", r"discovery",
    r"go[- ]to[- ]market", r"product[- ]market fit", r"\bpmf\b",
    r"customer insights", r"\bokrs?\b", r"\bkpis?\b", r"\bmvp\b",
    r"product analytics", r"voice of the customer", r"\bvoc\b",
    r"requirements gathering", r"trade[- ]offs?", r"tradeoffs?",
    r"user stories", r"wireframe", r"product lifecycle", r"launch",
    r"\bbeta\b",
]
_PRODUCT_PATTERN = re.compile("|".join(_PRODUCT_KEYWORDS), re.IGNORECASE)
_PRODUCT_CAP = 3

# --- Scrappiness signal keywords (+1 each, cap 3) ---

_SCRAPPY_KEYWORDS = [
    r"scrappy", r"0[- ]to[- ]1", r"zero[- ]to[- ]one", r"founding",
    r"first pm", r"wear many hats", r"ambiguous", r"fast[- ]moving",
    r"builder", r"early[- ]stage", r"\bseed\b", r"series [ab]\b",
    r"entrepreneurial", r"resourceful", r"generalist", r"hands[- ]on",
    r"roll up your sleeves", r"roll up sleeves", r"self[- ]starter",
    r"startup", r"greenfield", r"from scratch", r"build from scratch",
    r"stand up", r"undefined", r"unstructured", r"ownership",
    r"lean team", r"small team", r"figure it out", r"doer", r"do-er",
    r"\byc\b", r"y combinator",
]
_SCRAPPY_PATTERN = re.compile("|".join(_SCRAPPY_KEYWORDS), re.IGNORECASE)
_SCRAPPY_CAP = 3

# --- Strategy & Ops signal keywords (+1 each, cap 3) ---

_STRATOPS_KEYWORDS = [
    r"strategic planning", r"business operations", r"biz ops",
    r"operational efficiency", r"revenue operations", r"revops",
    r"process improvement", r"executive", r"c[- ]suite", r"\bboard\b",
    r"investor", r"fundraising", r"operating model", r"p&l",
    r"profit and loss", r"budget", r"forecasting", r"special projects",
    r"initiatives", r"gtm strategy", r"go[- ]to[- ]market strategy",
    r"systems thinking", r"workflow", r"workflows", r"automation",
    r"stakeholder management", r"scaling", r"\bscale\b", r"playbook",
    r"operating cadence", r"\berp\b",
]
_STRATOPS_PATTERN = re.compile("|".join(_STRATOPS_KEYWORDS), re.IGNORECASE)
_STRATOPS_CAP = 3

# --- Industry exclusion ---

_EXCLUDE_INDUSTRY_PATTERN = re.compile(
    "|".join(re.escape(ind) for ind in EXCLUDED_INDUSTRIES), re.IGNORECASE
)

# --- Seniority penalties ---

_SENIORITY_RULES = [
    (re.compile(r"\bsenior\b", re.IGNORECASE), -1),
    (re.compile(r"\bstaff\b", re.IGNORECASE), -2),
    (re.compile(r"\bprincipal\b", re.IGNORECASE), -3),
    (re.compile(r"\bdirector\b", re.IGNORECASE), -3),
    (re.compile(r"\bvp\b", re.IGNORECASE), -3),
    (re.compile(r"\bvice president\b", re.IGNORECASE), -3),
    (re.compile(r"\bhead of\b", re.IGNORECASE), -2),
]

_HEAD_OF_GROWTH = re.compile(r"\bhead of growth\b", re.IGNORECASE)

# --- Negative signals (applied to description, cap total at -4) ---

_NEGATIVE_RULES = [
    # Years of experience gates: -2 each
    (re.compile(r"\b[7-9]\+\s*years?\b", re.IGNORECASE), -2),
    (re.compile(r"\b1[0-9]\+\s*years?\b", re.IGNORECASE), -2),
    (re.compile(r"\b15\+\s*years?\b", re.IGNORECASE), -2),
    # Degree requirements: -2 each
    (re.compile(r"computer science degree", re.IGNORECASE), -2),
    (re.compile(r"\bcs degree\b", re.IGNORECASE), -2),
    (re.compile(r"\bphd\b", re.IGNORECASE), -2),
    # Technical mismatch: -1 each
    (re.compile(r"\bdata science\b", re.IGNORECASE), -1),
    (re.compile(r"\bsystem design\b", re.IGNORECASE), -1),
    # People management: -1 each
    (re.compile(r"manage a team of", re.IGNORECASE), -1),
    (re.compile(r"\bdirect reports\b", re.IGNORECASE), -1),
    (re.compile(r"people management", re.IGNORECASE), -1),
    # Sales signals: -1 each
    (re.compile(r"\bquota\b", re.IGNORECASE), -1),
    (re.compile(r"enterprise sales", re.IGNORECASE), -1),
    (re.compile(r"cold outreach", re.IGNORECASE), -1),
    (re.compile(r"cold calling", re.IGNORECASE), -1),
]
_NEGATIVE_CAP = -4


def _score_seniority(title):
    """Return seniority penalty for a title. 'Head of Growth' is exempt."""
    if _HEAD_OF_GROWTH.search(title):
        return 0

    # Apply the worst (most negative) matching penalty
    worst = 0
    for pattern, penalty in _SENIORITY_RULES:
        if pattern.search(title):
            if penalty < worst:
                worst = penalty
    return worst


def _score_negative_signals(description):
    """Return negative signal penalty, capped at _NEGATIVE_CAP."""
    total = 0
    for pattern, penalty in _NEGATIVE_RULES:
        if pattern.search(description):
            total += penalty
    return max(total, _NEGATIVE_CAP)


def _count_signal_matches(pattern, text, cap):
    """Count unique keyword matches in text, capped."""
    matches = pattern.findall(text)
    return min(len(matches), cap)


def prescore_jobs(jobs, max_results=DEFAULT_MAX):
    """Score jobs 0-19 and return top max_results sorted by score descending."""
    scored = []

    for job in jobs:
        desc = job.get("description", "")
        company = job.get("company", "")
        title = job.get("title", "")
        location = job.get("location", "")

        # Hard filter: excluded industries (check first 500 chars of desc + company name)
        if _EXCLUDE_INDUSTRY_PATTERN.search(desc[:500]):
            continue
        if _EXCLUDE_INDUSTRY_PATTERN.search(company):
            continue

        score = 0

        # Location match (+3, cap 3)
        if _LOC_PATTERN.search(location):
            score += 3

        # Title match (+3, cap 3)
        if title_matches_target(title):
            score += 3

        # Growth signals (+1 each, cap 4)
        score += _count_signal_matches(_GROWTH_PATTERN, desc, _GROWTH_CAP)

        # Product signals (+1 each, cap 3)
        score += _count_signal_matches(_PRODUCT_PATTERN, desc, _PRODUCT_CAP)

        # Scrappiness signals (+1 each, cap 3)
        score += _count_signal_matches(_SCRAPPY_PATTERN, desc, _SCRAPPY_CAP)

        # Strategy & Ops signals (+1 each, cap 3)
        score += _count_signal_matches(_STRATOPS_PATTERN, desc, _STRATOPS_CAP)

        # Seniority penalty
        score += _score_seniority(title)

        # Negative signals
        score += _score_negative_signals(desc)

        entry = {
            "title": title,
            "company": company,
            "location": location,
            "url": job.get("url", ""),
            "source": job.get("source", ""),
            "description": desc[:DESC_TRUNCATE],
            "prescore": score,
        }
        scored.append(entry)

    scored.sort(key=lambda x: x["prescore"], reverse=True)
    return scored[:max_results]


def run():
    """Read scraped_jobs.json, pre-score, and write filtered_jobs.json."""
    scraped_path = Path("data/scraped_jobs.json")
    if not scraped_path.exists():
        print("No scraped_jobs.json found")
        return

    with open(scraped_path) as f:
        data = json.load(f)

    jobs = data.get("jobs", [])
    filtered = prescore_jobs(jobs)

    output = {
        "timestamp": data.get("timestamp", ""),
        "total_scraped": data.get("total_scraped", 0),
        "unique_jobs": data.get("unique_jobs", 0),
        "filtered_count": len(filtered),
        "errors": data.get("errors", []),
        "elapsed_seconds": data.get("elapsed_seconds", 0),
        "jobs": filtered,
    }

    out_path = Path("data/filtered_jobs.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Pre-scored {len(jobs)} -> {len(filtered)} jobs -> data/filtered_jobs.json")


if __name__ == "__main__":
    run()
