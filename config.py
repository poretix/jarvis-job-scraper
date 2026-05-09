import os
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

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

SCRAPE_TIMEOUT = 30
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
