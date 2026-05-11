import os
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
DREAMWORK_API_KEY = os.getenv("DREAMWORK_API_KEY")

SCORE_THRESHOLD_FULL = 7
SCORE_THRESHOLD_MENTION = 5
MAX_FULL_POSTS = 20

LOCATIONS = ["San Francisco", "New York", "NYC", "Remote"]

EXCLUDED_INDUSTRIES = ["healthcare", "insurance", "health tech", "healthtech"]

ROLE_TITLES = {
    "growth": [
        "Growth Manager",
        "Growth Associate",
        "Growth Analyst",
        "Growth Lead",
        "Growth PM",
        "Growth Product Manager",
        "Growth Marketing Manager",
        "Head of Growth",
        "Lifecycle Marketing Manager",
    ],
    "product": [
        "Product Manager",
        "PM",
        "Associate Product Manager",
        "Associate PM",
        "APM",
        "Founding Product Manager",
        "Founding PM",
        "First PM",
        "Product Lead",
        "Product Growth Manager",
        "Product Operations Manager",
        "Product Operations",
    ],
    "strategy_ops": [
        "Chief of Staff",
        "Strategy & Operations",
        "Strategy and Operations",
        "Business Operations Manager",
        "Business Operations",
        "Biz Ops",
        "Revenue Operations",
        "RevOps",
        "GTM Operations",
        "GTM Ops",
        "Strategic Initiatives",
    ],
    "adjacent": [
        "Partnerships Manager",
        "Business Development Manager",
        "Partner Operations",
        "Product Marketing Manager",
        "Marketplace Manager",
        "GTM Manager",
        "GTM Lead",
        "Solutions Manager",
        "Community Manager",
    ],
}

TITLE_ABBREVIATIONS = {
    "PM": "Product Manager",
    "APM": "Associate Product Manager",
    "Biz Ops": "Business Operations",
    "RevOps": "Revenue Operations",
    "GTM": "Go-to-Market",
}

BRAVE_SEARCH_QUERIES = [
    '"{title}" startup hiring site:greenhouse.io',
    '"{title}" startup hiring site:lever.co',
    '"{title}" startup hiring site:jobs.ashbyhq.com',
    '"{title}" YC startup hiring 2026',
    '"{title}" seed series A hiring remote',
    '"{title}" startup job board SF NYC',
]

BRAVE_LINKEDIN_QUERIES = [
    'site:linkedin.com/jobs/view "{title}" startup',
    'site:linkedin.com/jobs/view "{title}" remote 2026',
]

SCRAPE_TIMEOUT = 30

import re

_TARGET_PATTERNS = []
for titles in ROLE_TITLES.values():
    for t in titles:
        _TARGET_PATTERNS.append(re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE))

_EXCLUDE_ROLE_WORDS = re.compile(
    r"\b(sales development rep|business development rep|"
    r"software engineer|software developer|"
    r"engineer|developer|designer|recruiter|accountant|bookkeeper|"
    r"nurse|therapist|physician|sdr|bdr)\b", re.IGNORECASE
)


def title_matches_target(job_title):
    for pattern in _TARGET_PATTERNS:
        if pattern.search(job_title):
            return True
    return False
PIPELINE_SOURCES = [
    "brave_search",
    "greenhouse",
    "lever",
    "ashby",
    "yc_startup",
    "startups_gallery",
    "remoteok",
    "himalayas",
    "builtin",
    "hn_hiring",
]
