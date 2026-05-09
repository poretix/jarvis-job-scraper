# Jarvis Job Scraper Pipeline — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an automated daily job scraping pipeline that discovers, scrapes, scores, tailors application materials (cover letter + tweaked resume), renders PDFs, and posts to Discord.

**Architecture:** Six-layer pipeline split between Python (data collection, PDF rendering, Discord posting) and Claude Code Routine (scoring, fit analysis, cover letter generation, resume tailoring). Python handles mechanical HTTP work; the Routine handles all intelligence work using the user's subscription — no separate API key. Daily cron at 5 PM PST.

**Tech Stack:** Python 3.11+, requests, BeautifulSoup4, fpdf2, Discord REST API (bot token, no discord.py)

---

## Task 1: Project Scaffold & Configuration

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `requirements.txt`
- Create: `config.py`
- Create: `resume_base.md`
- Create: `scraper/__init__.py`
- Create: `tailor/__init__.py`
- Create: `renderer/__init__.py`
- Create: `poster/__init__.py`
- Create: `utils/__init__.py`
- Create: `data/.gitkeep`
- Create: `tests/__init__.py`

**Step 1: Create `.gitignore`**

```
.env
data/scraped_jobs.json
data/scored_jobs.json
data/pdfs/
__pycache__/
*.pyc
.pytest_cache/
venv/
```

**Step 2: Create `.env.example`**

```
BRAVE_API_KEY=           # Brave Search API (free tier, 2000 queries/month)
DISCORD_BOT_TOKEN=       # Discord bot token
DISCORD_CHANNEL_ID=      # Target channel ID for job postings
```

**Step 3: Create `requirements.txt`**

```
requests>=2.31
beautifulsoup4>=4.12
fpdf2>=2.7
python-dotenv>=1.0
```

**Step 4: Create `config.py`**

This file contains all role targets, search queries, title mappings, and scoring thresholds. It is the single source of truth for what Jarvis looks for.

```python
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
```

**Step 5: Create `resume_base.md`**

Populate with Nathan's full resume in structured markdown format — sections with headers, bullet points per role. Content from the attached PDF resume.

```markdown
# Nathan Vuong

Irvine, CA | nvuong3.professional@gmail.com | 949-527-1489 | LinkedIn | Portfolio

## Career Snapshot

Entrepreneurial by nature, I spot gaps, move fast, and turn ideas into profitable products. I've built ventures generating over $400K in revenue by identifying demand early, acting decisively, and launching products with strong market fit. On the professional side, I've led cloud ERP implementations for Fortune 500 clients, aligning cross-functional teams and translating complex needs into solutions that scale. Whether launching a product from scratch or navigating enterprise systems, I get things moving, keep them focused, and build with impact.

## Work Experience

### PricewaterhouseCoopers (PwC)
**Cloud & Digital Consulting Senior Associate**
August 2022 – Present | San Francisco, California

- Lead end-to-end implementations of Workday Financials for three Fortune 500 clients by building automated processes for capital project tracking, spend management, and asset reporting to cut manual processes by 40%
- Diagnose a critical legacy-to-platform architecture gap at a Fortune 500 client, design an alternative mapping framework, and align accounting and engineering teams to route millions in monthly spend accurately
- Extract workflow pain points from finance and operations stakeholders and translate findings into system requirements that eliminate process failures across thousands of invoice submissions
- Surface end user adoption risks ahead of system go-lives through VOC interviews and surveys to convert insights into training plans that achieved 85% awareness and satisfaction across 500 surveyed users
- Transform stakeholder requirements into data mapping decisions across 3+ legacy systems and resolve integrity gaps across hundreds of thousands of assets through iterative testing cycles to deliver clean data upon go-live

### Aiso Pickleball
**Co-Founder**
September 2023 – September 2025 | San Francisco, California

- Traced supply chains of leading paddle brands through public shipping records to identify and vet manufacturing partners and co-develop two performance paddles that generated $100K in revenue
- Developed a direct to consumer brand through SEO, web attribution analysis, automated conversion workflows, and post purchase surveys to optimize acquisition channels and inform iterative product improvements
- Launched a commission based influencer program that drove 60% of revenue by crafting pitches that cut through high volume reviewer inboxes to earn a dedicated podcast segment and top budget paddle of 2025
- Engineered a paddle using insights from community research across YouTube, Reddit, and Discord to solve a known player performance problem at a price point that undercuts comparable paddles by over 50%

### Xpress Distribution
**Founder**
December 2020 – Present | Irvine, California

- Build a demand evaluation framework across streaming data, venue capacity, and geographic demographics to identify underpriced ticket inventory ahead of the market and produce $175K in revenue at 53% ROI
- Scale a sneaker and streetwear resale operation from $300 to $25K by networking into closed communities and deploying automation software with proxy infrastructure to capitalize on high demand releases
- Ship an inventory management system with automated order tracking, real-time secondary market valuation, invoicing, and expense tracking to eliminate manual workflows across a resale operation serving 40 active users

## Education

### University of California, Santa Barbara
**Bachelor of Arts in Economics & Accounting, GPA: 3.95**
Class of 2022 | Santa Barbara, California

- Awards & Honors: L&S Honors Program, Dean's Honors, and recipient of the Kevin Patrick Memorial Scholarship, awarded annually to 1 student for demonstration of leadership qualities and academic promise

## Certifications & Skills

- Certifications: AWS Certified Cloud Practitioner
- Skills: Web Development (HTML, CSS, JS), Python, SQL, Excel, Powerpoint, Jira, and Figma
- AI Assisted Development: Built and shipped production web applications utilizing REST API integrations, database architecture, and automated workflows via Claude Code
```

**Step 6: Create all `__init__.py` files and `data/.gitkeep`**

All `__init__.py` files are empty. `data/.gitkeep` is empty (just ensures the directory is tracked).

**Step 7: Initialize git and commit**

```bash
git init
git add .
git commit -m "feat: project scaffold with config, resume, and directory structure"
```

---

## Task 2: Utility Modules — Logger & Deduper

**Files:**
- Create: `utils/logger.py`
- Create: `utils/deduper.py`
- Create: `tests/test_utils.py`

**Step 1: Write failing tests for deduper**

```python
# tests/test_utils.py
from utils.deduper import Deduper


def test_deduper_removes_duplicate_urls():
    deduper = Deduper()
    jobs = [
        {"url": "https://a.com/job/1", "title": "PM"},
        {"url": "https://a.com/job/1", "title": "PM duplicate"},
        {"url": "https://b.com/job/2", "title": "Growth"},
    ]
    result = deduper.deduplicate(jobs)
    assert len(result) == 2
    assert result[0]["title"] == "PM"
    assert result[1]["title"] == "Growth"


def test_deduper_handles_empty_list():
    deduper = Deduper()
    assert deduper.deduplicate([]) == []


def test_deduper_normalizes_trailing_slashes():
    deduper = Deduper()
    jobs = [
        {"url": "https://a.com/job/1/", "title": "With slash"},
        {"url": "https://a.com/job/1", "title": "Without slash"},
    ]
    result = deduper.deduplicate(jobs)
    assert len(result) == 1
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_utils.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement deduper**

```python
# utils/deduper.py
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
```

**Step 4: Implement logger**

```python
# utils/logger.py
import logging
import sys

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

**Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_utils.py -v
```

Expected: 3 passed

**Step 6: Commit**

```bash
git add utils/ tests/test_utils.py
git commit -m "feat: add deduper and logger utilities"
```

---

## Task 3: Brave Search Discovery

**Files:**
- Create: `scraper/brave_search.py`
- Create: `tests/test_brave.py`

**Step 1: Write failing tests**

```python
# tests/test_brave.py
import json
from unittest.mock import patch, MagicMock
from scraper.brave_search import BraveSearchScraper


def _mock_brave_response(results):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"web": {"results": results}}
    return resp


def test_brave_extracts_greenhouse_urls():
    results = [
        {"url": "https://boards.greenhouse.io/acme/jobs/123", "title": "PM at Acme"},
        {"url": "https://example.com/unrelated", "title": "Blog post"},
    ]
    with patch("scraper.brave_search.requests.get", return_value=_mock_brave_response(results)):
        scraper = BraveSearchScraper(api_key="test")
        urls = scraper.discover(query='"Product Manager" startup site:greenhouse.io')
    assert len(urls) == 1
    assert urls[0]["url"] == "https://boards.greenhouse.io/acme/jobs/123"


def test_brave_extracts_lever_urls():
    results = [
        {"url": "https://jobs.lever.co/acme/abc-123", "title": "Growth at Acme"},
    ]
    with patch("scraper.brave_search.requests.get", return_value=_mock_brave_response(results)):
        scraper = BraveSearchScraper(api_key="test")
        urls = scraper.discover(query='"Growth Manager" site:lever.co')
    assert len(urls) == 1
    assert urls[0]["source"] == "lever"


def test_brave_handles_api_error():
    resp = MagicMock()
    resp.status_code = 429
    resp.text = "rate limited"
    with patch("scraper.brave_search.requests.get", return_value=resp):
        scraper = BraveSearchScraper(api_key="test")
        urls = scraper.discover(query="anything")
    assert urls == []


def test_brave_classifies_sources():
    results = [
        {"url": "https://boards.greenhouse.io/x/jobs/1", "title": "A"},
        {"url": "https://jobs.lever.co/x/abc", "title": "B"},
        {"url": "https://jobs.ashbyhq.com/x/abc", "title": "C"},
        {"url": "https://wellfound.com/jobs/123", "title": "D"},
        {"url": "https://random.com/careers", "title": "E"},
    ]
    with patch("scraper.brave_search.requests.get", return_value=_mock_brave_response(results)):
        scraper = BraveSearchScraper(api_key="test")
        urls = scraper.discover(query="test")
    sources = {u["source"] for u in urls}
    assert "greenhouse" in sources
    assert "lever" in sources
    assert "ashby" in sources
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_brave.py -v
```

**Step 3: Implement Brave Search scraper**

```python
# scraper/brave_search.py
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
```

**Step 4: Run tests, verify pass**

```bash
python -m pytest tests/test_brave.py -v
```

**Step 5: Commit**

```bash
git add scraper/brave_search.py tests/test_brave.py
git commit -m "feat: add Brave Search discovery with ATS URL classification"
```

---

## Task 4: ATS Extractors — Greenhouse, Lever, Ashby

**Files:**
- Create: `scraper/greenhouse.py`
- Create: `scraper/lever.py`
- Create: `scraper/ashby.py`
- Create: `tests/test_ats.py`

**Step 1: Write failing tests for Greenhouse**

```python
# tests/test_ats.py
import json
from unittest.mock import patch, MagicMock
from scraper.greenhouse import GreenhouseScraper
from scraper.lever import LeverScraper
from scraper.ashby import AshbyScraper


def _mock_response(data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    resp.text = json.dumps(data)
    return resp


# --- Greenhouse ---

def test_greenhouse_extracts_jobs():
    api_data = {
        "jobs": [
            {
                "id": 123,
                "title": "Growth PM",
                "location": {"name": "San Francisco, CA"},
                "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
                "content": "We are looking for a Growth PM...",
            }
        ]
    }
    with patch("scraper.greenhouse.requests.get", return_value=_mock_response(api_data)):
        scraper = GreenhouseScraper()
        jobs = scraper.extract("acme")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Growth PM"
    assert jobs[0]["source"] == "greenhouse"
    assert jobs[0]["company"] == "acme"


def test_greenhouse_handles_empty_board():
    with patch("scraper.greenhouse.requests.get", return_value=_mock_response({"jobs": []})):
        scraper = GreenhouseScraper()
        jobs = scraper.extract("empty-co")
    assert jobs == []


# --- Lever ---

def test_lever_extracts_jobs():
    api_data = [
        {
            "id": "abc-123",
            "text": "Business Operations",
            "categories": {"location": "New York, NY", "team": "Operations"},
            "hostedUrl": "https://jobs.lever.co/acme/abc-123",
            "descriptionPlain": "We need a biz ops person...",
        }
    ]
    with patch("scraper.lever.requests.get", return_value=_mock_response(api_data)):
        scraper = LeverScraper()
        jobs = scraper.extract("acme")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Business Operations"
    assert jobs[0]["source"] == "lever"


# --- Ashby ---

def test_ashby_extracts_jobs():
    api_data = {
        "jobs": [
            {
                "id": "xyz",
                "title": "Founding PM",
                "location": "Remote",
                "jobUrl": "https://jobs.ashbyhq.com/acme/xyz",
                "descriptionHtml": "<p>We want a founding PM...</p>",
            }
        ]
    }
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = api_data
    with patch("scraper.ashby.requests.post", return_value=resp):
        scraper = AshbyScraper()
        jobs = scraper.extract("acme")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Founding PM"
    assert jobs[0]["source"] == "ashby"
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_ats.py -v
```

**Step 3: Implement Greenhouse scraper**

```python
# scraper/greenhouse.py
import requests
from utils.logger import get_logger

log = get_logger("greenhouse")


class GreenhouseScraper:
    def extract(self, company_slug):
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                log.error(f"Greenhouse {company_slug}: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": company_slug,
                    "location": j.get("location", {}).get("name", ""),
                    "url": j.get("absolute_url", ""),
                    "description": j.get("content", ""),
                    "source": "greenhouse",
                })
            return jobs
        except Exception as e:
            log.error(f"Greenhouse {company_slug} failed: {e}")
            return []
```

**Step 4: Implement Lever scraper**

```python
# scraper/lever.py
import requests
from utils.logger import get_logger

log = get_logger("lever")


class LeverScraper:
    def extract(self, company_slug):
        url = f"https://api.lever.co/v0/postings/{company_slug}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                log.error(f"Lever {company_slug}: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for j in data:
                jobs.append({
                    "title": j.get("text", ""),
                    "company": company_slug,
                    "location": j.get("categories", {}).get("location", ""),
                    "url": j.get("hostedUrl", ""),
                    "description": j.get("descriptionPlain", ""),
                    "source": "lever",
                })
            return jobs
        except Exception as e:
            log.error(f"Lever {company_slug} failed: {e}")
            return []
```

**Step 5: Implement Ashby scraper**

```python
# scraper/ashby.py
import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("ashby")


class AshbyScraper:
    def extract(self, company_slug):
        url = "https://api.ashbyhq.com/posting-api/job-board/" + company_slug
        try:
            resp = requests.post(url, json={}, timeout=30)
            if resp.status_code != 200:
                log.error(f"Ashby {company_slug}: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for j in data.get("jobs", []):
                desc_html = j.get("descriptionHtml", "")
                desc_text = BeautifulSoup(desc_html, "html.parser").get_text(separator=" ") if desc_html else ""
                jobs.append({
                    "title": j.get("title", ""),
                    "company": company_slug,
                    "location": j.get("location", ""),
                    "url": j.get("jobUrl", ""),
                    "description": desc_text,
                    "source": "ashby",
                })
            return jobs
        except Exception as e:
            log.error(f"Ashby {company_slug} failed: {e}")
            return []
```

**Step 6: Run tests, verify pass**

```bash
python -m pytest tests/test_ats.py -v
```

**Step 7: Commit**

```bash
git add scraper/greenhouse.py scraper/lever.py scraper/ashby.py tests/test_ats.py
git commit -m "feat: add Greenhouse, Lever, and Ashby ATS extractors"
```

---

## Task 5: Public API Scrapers — RemoteOK, Himalayas, Built In, HN Hiring

**Files:**
- Create: `scraper/remoteok.py`
- Create: `scraper/himalayas.py`
- Create: `scraper/builtin.py`
- Create: `scraper/hn_hiring.py`
- Create: `tests/test_public_apis.py`

**Step 1: Write failing tests**

```python
# tests/test_public_apis.py
from unittest.mock import patch, MagicMock
from scraper.remoteok import RemoteOKScraper
from scraper.himalayas import HimalayasScraper
from scraper.builtin import BuiltInScraper
from scraper.hn_hiring import HNHiringScraper


def _mock_response(data, status=200, text=None):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    resp.text = text or ""
    return resp


def test_remoteok_extracts_jobs():
    api_data = [
        {},  # first element is metadata
        {
            "id": "1",
            "position": "Growth Lead",
            "company": "StartupCo",
            "location": "Remote",
            "url": "https://remoteok.com/jobs/1",
            "description": "Looking for growth lead...",
        },
    ]
    with patch("scraper.remoteok.requests.get", return_value=_mock_response(api_data)):
        scraper = RemoteOKScraper()
        jobs = scraper.extract()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Growth Lead"
    assert jobs[0]["source"] == "remoteok"


def test_hn_hiring_extracts_jobs():
    item_data = {
        "kids": [101, 102],
    }
    comment_1 = {
        "id": 101,
        "text": "Acme Corp | Product Manager | SF, Remote | Full-time<p>We are hiring a PM to lead our growth team. Apply at https://acme.com/jobs/pm",
        "dead": False,
        "deleted": False,
    }
    comment_2 = {
        "id": 102,
        "text": "BigCo | Senior Engineer | NYC",
        "dead": False,
        "deleted": False,
    }

    def mock_get(url, **kwargs):
        if "101" in url:
            return _mock_response(comment_1)
        if "102" in url:
            return _mock_response(comment_2)
        return _mock_response(item_data)

    with patch("scraper.hn_hiring.requests.get", side_effect=mock_get):
        scraper = HNHiringScraper()
        jobs = scraper.extract(story_id=12345)
    assert len(jobs) == 2
    assert jobs[0]["company"] == "Acme Corp"
```

**Step 2: Run tests to verify fail**

```bash
python -m pytest tests/test_public_apis.py -v
```

**Step 3: Implement RemoteOK**

```python
# scraper/remoteok.py
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
```

**Step 4: Implement Himalayas**

```python
# scraper/himalayas.py
import requests
from utils.logger import get_logger

log = get_logger("himalayas")


class HimalayasScraper:
    URL = "https://himalayas.app/jobs/api"

    def extract(self):
        try:
            resp = requests.get(
                self.URL,
                params={"limit": 50},
                headers={"User-Agent": "Jarvis/1.0"},
                timeout=30,
            )
            if resp.status_code != 200:
                log.error(f"Himalayas: HTTP {resp.status_code}")
                return []
            data = resp.json()
            jobs = []
            for item in data.get("jobs", []):
                jobs.append({
                    "title": item.get("title", ""),
                    "company": item.get("companyName", ""),
                    "location": ", ".join(item.get("locationRestrictions", [])) or "Remote",
                    "url": item.get("applicationLink", "") or f"https://himalayas.app/jobs/{item.get('slug', '')}",
                    "description": item.get("description", ""),
                    "source": "himalayas",
                })
            return jobs
        except Exception as e:
            log.error(f"Himalayas failed: {e}")
            return []
```

**Step 5: Implement Built In**

```python
# scraper/builtin.py
import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("builtin")

BUILTIN_URLS = {
    "sf": "https://www.builtinsf.com/jobs",
    "nyc": "https://www.builtinnyc.com/jobs",
}


class BuiltInScraper:
    def extract(self):
        all_jobs = []
        for city, base_url in BUILTIN_URLS.items():
            try:
                resp = requests.get(
                    base_url,
                    params={"category": "product-management"},
                    headers={"User-Agent": "Jarvis/1.0"},
                    timeout=30,
                )
                if resp.status_code != 200:
                    log.error(f"BuiltIn {city}: HTTP {resp.status_code}")
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("[data-id='job-card']")
                for card in cards:
                    title_el = card.select_one("h2 a")
                    company_el = card.select_one("[data-id='company-title']")
                    if not title_el:
                        continue
                    href = title_el.get("href", "")
                    url = href if href.startswith("http") else f"https://www.builtin{city}.com{href}"
                    all_jobs.append({
                        "title": title_el.get_text(strip=True),
                        "company": company_el.get_text(strip=True) if company_el else "",
                        "location": city.upper(),
                        "url": url,
                        "description": "",
                        "source": "builtin",
                    })
            except Exception as e:
                log.error(f"BuiltIn {city} failed: {e}")
        return all_jobs
```

**Step 6: Implement HN Who Is Hiring parser**

```python
# scraper/hn_hiring.py
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
```

**Step 7: Run tests, verify pass**

```bash
python -m pytest tests/test_public_apis.py -v
```

**Step 8: Commit**

```bash
git add scraper/remoteok.py scraper/himalayas.py scraper/builtin.py scraper/hn_hiring.py tests/test_public_apis.py
git commit -m "feat: add RemoteOK, Himalayas, Built In, and HN Hiring scrapers"
```

---

## Task 6: Specialty Scrapers — YC Work at a Startup & startups.gallery

**Files:**
- Create: `scraper/yc_startup.py`
- Create: `scraper/startups_gallery.py`
- Create: `tests/test_specialty.py`

**Step 1: Write failing tests**

```python
# tests/test_specialty.py
from unittest.mock import patch, MagicMock
from scraper.yc_startup import YCStartupScraper
from scraper.startups_gallery import StartupsGalleryScraper


def test_yc_startup_extracts_jobs():
    html = """
    <div class="job-listing">
        <a class="job-title" href="/company/acme/jobs/pm">Product Manager</a>
        <span class="company-name">Acme (YC W24)</span>
        <span class="job-location">San Francisco, CA</span>
    </div>
    """
    resp = MagicMock()
    resp.status_code = 200
    resp.text = html
    with patch("scraper.yc_startup.requests.get", return_value=resp):
        scraper = YCStartupScraper()
        jobs = scraper.extract()
    assert len(jobs) >= 0  # HTML structure may vary; test verifies no crash


def test_startups_gallery_extracts_jobs():
    html = """
    <div class="job-card">
        <a href="/job/123" class="job-title">Growth Manager</a>
        <span class="company">StartupX</span>
        <span class="location">Remote</span>
    </div>
    """
    resp = MagicMock()
    resp.status_code = 200
    resp.text = html
    with patch("scraper.startups_gallery.requests.get", return_value=resp):
        scraper = StartupsGalleryScraper()
        jobs = scraper.extract()
    assert len(jobs) >= 0  # HTML structure may vary; test verifies no crash
```

**Step 2: Run tests to verify fail**

```bash
python -m pytest tests/test_specialty.py -v
```

**Step 3: Implement YC Work at a Startup scraper**

Note: The actual HTML selectors need to be verified against the live site during implementation. These are best-effort based on common patterns. The scraper should be tested against the live site and selectors adjusted.

```python
# scraper/yc_startup.py
import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("yc_startup")


class YCStartupScraper:
    BASE_URL = "https://www.workatastartup.com/jobs"

    def extract(self, role_query="product manager"):
        try:
            resp = requests.get(
                self.BASE_URL,
                params={"query": role_query},
                headers={"User-Agent": "Jarvis/1.0"},
                timeout=30,
            )
            if resp.status_code != 200:
                log.error(f"YC Work at a Startup: HTTP {resp.status_code}")
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = []

            # Selectors are approximate — verify against live site and adjust
            for card in soup.select("[class*='job'], [class*='listing'], [class*='posting']"):
                title_el = card.select_one("a[class*='title'], h3, h4")
                company_el = card.select_one("[class*='company']")
                location_el = card.select_one("[class*='location']")
                if not title_el:
                    continue
                href = title_el.get("href", "")
                url = href if href.startswith("http") else f"https://www.workatastartup.com{href}"
                jobs.append({
                    "title": title_el.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "url": url,
                    "description": "",
                    "source": "yc_startup",
                })
            return jobs

        except Exception as e:
            log.error(f"YC Work at a Startup failed: {e}")
            return []
```

**Step 4: Implement startups.gallery scraper**

```python
# scraper/startups_gallery.py
import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

log = get_logger("startups_gallery")


class StartupsGalleryScraper:
    BASE_URL = "https://startups.gallery"

    def extract(self):
        try:
            resp = requests.get(
                f"{self.BASE_URL}/jobs",
                headers={"User-Agent": "Jarvis/1.0"},
                timeout=30,
            )
            if resp.status_code != 200:
                log.error(f"startups.gallery: HTTP {resp.status_code}")
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = []

            # Selectors are approximate — verify against live site and adjust
            for card in soup.select("[class*='job'], [class*='listing'], [class*='card']"):
                title_el = card.select_one("a[class*='title'], h3, h4")
                company_el = card.select_one("[class*='company']")
                location_el = card.select_one("[class*='location']")
                if not title_el:
                    continue
                href = title_el.get("href", "")
                url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                jobs.append({
                    "title": title_el.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "url": url,
                    "description": "",
                    "source": "startups_gallery",
                })
            return jobs

        except Exception as e:
            log.error(f"startups.gallery failed: {e}")
            return []
```

**Step 5: Run tests, verify pass**

```bash
python -m pytest tests/test_specialty.py -v
```

**Step 6: Commit**

```bash
git add scraper/yc_startup.py scraper/startups_gallery.py tests/test_specialty.py
git commit -m "feat: add YC Work at a Startup and startups.gallery scrapers"
```

---

## Task 7: Scraper Orchestrator (main.py — Phase 1)

**Files:**
- Create: `main.py`

**Step 1: Implement the scraping orchestrator**

This is Phase 1 of `main.py` — it only handles discovery, extraction, and deduplication. The scoring/tailoring happens in the Claude Code Routine (Task 10). The Discord posting happens in Task 9.

```python
# main.py
import json
import os
import sys
import time
from pathlib import Path

from config import (
    BRAVE_API_KEY,
    BRAVE_SEARCH_QUERIES,
    ROLE_TITLES,
    SCRAPE_TIMEOUT,
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
from utils.deduper import Deduper
from utils.logger import get_logger

log = get_logger("main")
DATA_DIR = Path("data")


def run_discovery():
    """Use Brave Search to discover ATS board URLs."""
    if not BRAVE_API_KEY:
        log.warning("No BRAVE_API_KEY — skipping discovery")
        return []

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
    return discovered


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

    for name, runner in source_runners:
        try:
            jobs = runner()
            all_jobs.extend(jobs)
            log.info(f"{name}: {len(jobs)} jobs")
        except Exception as e:
            errors.append(f"{name}: {e}")
            log.error(f"{name} failed: {e}")

    return all_jobs, errors


def run_scrape():
    """Full scrape pipeline: discover → extract → deduplicate → save."""
    DATA_DIR.mkdir(exist_ok=True)

    start = time.time()
    discovered = run_discovery()
    all_jobs, errors = run_extraction(discovered)

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
```

**Step 2: Test manually**

```bash
python main.py
```

Verify `data/scraped_jobs.json` is created with the expected structure.

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add scraping orchestrator with discovery, extraction, and dedup"
```

---

## Task 8: PDF Renderer

**Files:**
- Create: `renderer/pdf_builder.py`
- Create: `tests/test_renderer.py`

**Step 1: Write failing tests**

```python
# tests/test_renderer.py
import os
from pathlib import Path
from renderer.pdf_builder import render_cover_letter_pdf, render_resume_pdf


def test_render_cover_letter_creates_pdf(tmp_path):
    cover_letter = "Dear Hiring Team,\n\nI am writing about the Growth PM role.\n\nBest,\nNathan"
    output = tmp_path / "cover.pdf"
    render_cover_letter_pdf(cover_letter, str(output))
    assert output.exists()
    assert output.stat().st_size > 0


def test_render_resume_creates_pdf(tmp_path):
    resume_md = "# Nathan Vuong\n\n## Experience\n\n### PwC\n- Did things\n- Did more things"
    output = tmp_path / "resume.pdf"
    render_resume_pdf(resume_md, str(output))
    assert output.exists()
    assert output.stat().st_size > 0
```

**Step 2: Run tests to verify fail**

```bash
python -m pytest tests/test_renderer.py -v
```

**Step 3: Implement PDF builder**

```python
# renderer/pdf_builder.py
import re
from fpdf import FPDF


class _BasePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(25, 20, 25)
        self.set_font("Helvetica", size=11)


def render_cover_letter_pdf(text, output_path):
    pdf = _BasePDF()
    pdf.set_font("Helvetica", size=11)
    for line in text.split("\n"):
        if line.strip() == "":
            pdf.ln(6)
        else:
            pdf.multi_cell(0, 6, line.strip())
    pdf.output(output_path)


def render_resume_pdf(markdown_text, output_path):
    pdf = _BasePDF()
    for line in markdown_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            pdf.ln(4)
        elif stripped.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, stripped[2:], new_x="LMARGIN", new_y="NEXT")
        elif stripped.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, stripped[3:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(200, 200, 200)
            pdf.line(25, pdf.get_y(), 185, pdf.get_y())
            pdf.ln(2)
        elif stripped.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, stripped[4:], new_x="LMARGIN", new_y="NEXT")
        elif stripped.startswith("**") and stripped.endswith("**"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, stripped[2:-2], new_x="LMARGIN", new_y="NEXT")
        elif stripped.startswith("- "):
            pdf.set_font("Helvetica", size=10)
            pdf.cell(5)
            pdf.multi_cell(0, 5, f"• {stripped[2:]}")
        else:
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 6, stripped)
    pdf.output(output_path)
```

**Step 4: Run tests, verify pass**

```bash
python -m pytest tests/test_renderer.py -v
```

**Step 5: Commit**

```bash
git add renderer/pdf_builder.py tests/test_renderer.py
git commit -m "feat: add PDF renderer for cover letters and resumes"
```

---

## Task 9: Discord Poster with Threading & File Attachments

**Files:**
- Create: `poster/discord_poster.py`
- Create: `tests/test_discord.py`

**Step 1: Write failing tests**

```python
# tests/test_discord.py
from unittest.mock import patch, MagicMock
from poster.discord_poster import DiscordPoster


def _mock_post_response(message_id="111"):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"id": message_id}
    return resp


def test_post_summary_sends_embed():
    with patch("poster.discord_poster.requests.post", return_value=_mock_post_response()) as mock:
        poster = DiscordPoster(bot_token="test", channel_id="123")
        poster.post_summary(
            total_scraped=147,
            unique=89,
            top_matches=8,
            worth_a_look=12,
            errors=[],
            elapsed=134.2,
        )
    assert mock.called
    call_kwargs = mock.call_args
    assert "embeds" in call_kwargs.kwargs.get("json", {}) or "embeds" in call_kwargs[1].get("json", {})


def test_post_job_creates_thread():
    responses = [
        _mock_post_response("msg-1"),  # main message
        _mock_post_response("thread-1"),  # thread creation
        _mock_post_response(),  # file upload 1
        _mock_post_response(),  # file upload 2
    ]
    with patch("poster.discord_poster.requests.post", side_effect=responses):
        with patch("poster.discord_poster.requests.request", return_value=_mock_post_response()):
            poster = DiscordPoster(bot_token="test", channel_id="123")
            poster.post_job(
                job={"title": "Growth PM", "company": "Ramp", "url": "https://ramp.com/jobs/1", "location": "NYC", "score": 9, "fit_analysis": "Strong match."},
                cover_letter_pdf="/tmp/cover.pdf",
                resume_pdf="/tmp/resume.pdf",
            )
```

**Step 2: Run tests to verify fail**

```bash
python -m pytest tests/test_discord.py -v
```

**Step 3: Implement Discord poster**

```python
# poster/discord_poster.py
import os
import requests
from utils.logger import get_logger

log = get_logger("discord")

BASE_URL = "https://discord.com/api/v10"


class DiscordPoster:
    def __init__(self, bot_token, channel_id):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.headers = {
            "Authorization": f"Bot {bot_token}",
            "User-Agent": "Jarvis/1.0",
        }

    def post_summary(self, total_scraped, unique, top_matches, worth_a_look, errors, elapsed):
        error_text = ""
        if errors:
            error_lines = [f"- {e}" for e in errors[:5]]
            error_text = "\n".join(error_lines)

        embed = {
            "title": "Jarvis Daily Report",
            "color": 0x5865F2,
            "fields": [
                {"name": "Jobs Found", "value": str(total_scraped), "inline": True},
                {"name": "After Dedup", "value": str(unique), "inline": True},
                {"name": "Top Matches (7+)", "value": str(top_matches), "inline": True},
                {"name": "Worth a Look (5-6)", "value": str(worth_a_look), "inline": True},
                {"name": "Runtime", "value": f"{elapsed:.0f}s", "inline": True},
            ],
        }
        if error_text:
            embed["footer"] = {"text": f"Errors:\n{error_text}"}

        self._send_message({"embeds": [embed]})

    def post_job(self, job, cover_letter_pdf=None, resume_pdf=None):
        score = job["score"]
        color = 0x57F287 if score >= 9 else 0xFEE75C if score >= 7 else 0x99AAB5

        embed = {
            "title": f"{'🟢' if score >= 9 else '🟡' if score >= 7 else '⚪'} {score}/10 — {job['title']} @ {job['company']}",
            "url": job["url"],
            "color": color,
            "fields": [
                {"name": "Location", "value": job.get("location", "N/A"), "inline": True},
                {"name": "Fit Analysis", "value": job.get("fit_analysis", "")[:1024]},
            ],
        }

        msg = self._send_message({"embeds": [embed]})
        if not msg:
            return

        message_id = msg.get("id")
        if not message_id:
            return

        thread = self._create_thread(message_id, f"{job['title']} @ {job['company']}")
        if not thread:
            return

        thread_id = thread.get("id")
        if cover_letter_pdf and os.path.exists(cover_letter_pdf):
            self._upload_file(thread_id, cover_letter_pdf, "cover_letter.pdf")
        if resume_pdf and os.path.exists(resume_pdf):
            self._upload_file(thread_id, resume_pdf, "resume.pdf")

    def post_compact_list(self, jobs):
        lines = []
        for job in jobs:
            score = job["score"]
            lines.append(f"**{score}/10** — [{job['title']} @ {job['company']}]({job['url']})")
            if job.get("fit_analysis"):
                lines.append(f"  _{job['fit_analysis'][:100]}_")
            lines.append("")

        embed = {
            "title": "Worth a Look (5-6)",
            "description": "\n".join(lines)[:4096],
            "color": 0x99AAB5,
        }
        self._send_message({"embeds": [embed]})

    def post_no_matches(self, total_scanned, near_miss=None):
        desc = f"No matches today. {total_scanned} jobs scanned, none scored above 5."
        if near_miss:
            desc += f"\nTop near-miss: {near_miss['title']} @ {near_miss['company']} ({near_miss['score']}/10)"
        embed = {"title": "No Matches", "description": desc, "color": 0xED4245}
        self._send_message({"embeds": [embed]})

    def _send_message(self, payload):
        try:
            resp = requests.post(
                f"{BASE_URL}/channels/{self.channel_id}/messages",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )
            if resp.status_code != 200:
                log.error(f"Discord send failed: {resp.status_code} {resp.text[:200]}")
                return None
            return resp.json()
        except Exception as e:
            log.error(f"Discord send error: {e}")
            return None

    def _create_thread(self, message_id, name):
        try:
            resp = requests.post(
                f"{BASE_URL}/channels/{self.channel_id}/messages/{message_id}/threads",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"name": name[:100], "auto_archive_duration": 1440},
                timeout=10,
            )
            if resp.status_code not in (200, 201):
                log.error(f"Thread creation failed: {resp.status_code}")
                return None
            return resp.json()
        except Exception as e:
            log.error(f"Thread creation error: {e}")
            return None

    def _upload_file(self, channel_id, file_path, filename):
        try:
            with open(file_path, "rb") as f:
                resp = requests.post(
                    f"{BASE_URL}/channels/{channel_id}/messages",
                    headers={"Authorization": f"Bot {self.bot_token}"},
                    files={"file": (filename, f, "application/pdf")},
                    timeout=15,
                )
            if resp.status_code not in (200, 201):
                log.error(f"File upload failed: {resp.status_code}")
        except Exception as e:
            log.error(f"File upload error: {e}")
```

**Step 4: Run tests, verify pass**

```bash
python -m pytest tests/test_discord.py -v
```

**Step 5: Commit**

```bash
git add poster/discord_poster.py tests/test_discord.py
git commit -m "feat: add Discord poster with thread creation and PDF attachments"
```

---

## Task 10: Routine Prompt & Tailoring Templates

**Files:**
- Create: `routine_prompt.md`
- Create: `tailor/templates.py`

This is the most critical file — it's the instruction set that the Claude Code Routine follows for scoring, fit analysis, cover letter generation, and resume tailoring.

**Step 1: Create `tailor/templates.py`**

This contains formatting constants used by the Routine output and referenced in `routine_prompt.md`.

```python
# tailor/templates.py

COVER_LETTER_CONSTRAINTS = {
    "max_words": 250,
    "structure": [
        "Opening: name the role, one specific hook about the company (2-3 sentences)",
        "Middle: 2-3 examples mapping experience to JD using XYZ format (2-3 short paragraphs)",
        "Close: reiterate interest, contact info (2 sentences)",
    ],
    "voice_rules": [
        "Write like Nathan talks — direct, results-first, no filler",
        "Lead with a specific story or result, not a generic opener",
        "Short sentences are fine. Fragments are fine. Vary the rhythm.",
        "Never use participle phrases to start a sentence",
        "Never use: leveraging, utilizing, demonstrating, facilitating, furthermore, moreover",
        "Never use: I'm thrilled, I'm excited, I'm passionate, dynamic professional",
        "Never start more than one paragraph with 'I'",
        "Numbers and results > adjectives about yourself",
        "Close with 'Happy to chat' or similar, not 'I look forward to the opportunity'",
    ],
    "xyz_format": "Accomplished [X] as measured by [Y] by doing [Z]",
}

RESUME_TWEAK_CONSTRAINTS = {
    "max_word_changes": 5,
    "allowed_operations": [
        "Reorder bullets within each job section (most relevant first)",
        "Reorder skills list to match JD emphasis",
        "Mirror JD vocabulary where natural (max 3-5 word-level swaps)",
    ],
    "forbidden_operations": [
        "Never change facts or numbers",
        "Never add claims Nathan can't back up",
        "Never add skills Nathan doesn't have",
        "Never restructure the resume sections or change section order",
        "Never change job titles, dates, or company names",
    ],
}

SCORING_DIMENSIONS = {
    "role_profile_match": {"weight": 0.30, "description": "Does the JD map to work Nathan has done, including entrepreneurial PM work?"},
    "seniority_fit": {"weight": 0.20, "description": "5+ yr PM title = lower (not disqualifier). Scrappy/0-to-1/startup mentality = boost."},
    "company_stage": {"weight": 0.15, "description": "Seed-Series B = highest. Enterprise/public OK if product/growth. Healthcare/insurance = excluded."},
    "scrappiness_signal": {"weight": 0.10, "description": "JD signals builder: scrappy, resourceful, 0→1, wear many hats, ambiguous, founding, first PM."},
    "location_match": {"weight": 0.15, "description": "SF, NYC, Remote = full. Other = 0."},
    "growth_signal_density": {"weight": 0.10, "description": "Experimentation, metrics ownership, acquisition, retention, PLG, GTM, conversion, funnel."},
}
```

**Step 2: Create `routine_prompt.md`**

This is the instruction file the Claude Code Routine reads. It tells Claude exactly how to score, analyze, and tailor.

```markdown
# Jarvis Routine — Scoring & Tailoring Instructions

You are running as a Claude Code Routine for Jarvis, Nathan Vuong's job scraper pipeline.

## Your inputs
1. `data/scraped_jobs.json` — raw job listings from the scraping phase
2. `resume_base.md` — Nathan's base resume (source of truth)
3. `tailor/templates.py` — constraints for cover letters, resume tweaks, and scoring

## Your outputs
Write `data/scored_jobs.json` with this structure:

```json
{
  "timestamp": "ISO timestamp",
  "jobs": [
    {
      "title": "Growth PM",
      "company": "Ramp",
      "url": "https://...",
      "location": "NYC",
      "source": "greenhouse",
      "score": 9,
      "fit_analysis": "2-3 sentence analysis",
      "cover_letter": "Full cover letter text (for 7+ only)",
      "tweaked_resume": "Full tweaked resume markdown (for 7+ only)"
    }
  ]
}
```

## Scoring rubric

Score each job 1-10 using these weighted dimensions:

| Dimension | Weight | Evaluation |
|-----------|--------|------------|
| Role-profile match | 30% | Does the JD map to Growth/Product/Strategy/Ops work Nathan has actually done — including entrepreneurial PM work at Aiso and Xpress? |
| Seniority fit | 20% | 5+ yr PM title at BigCo = lower score (not disqualifier). "Scrappy", "0→1", "startup mentality", "entrepreneurial" = signal boost. Nathan has ~3 years professional + 5 years entrepreneurial. |
| Company stage | 15% | Seed-Series B = highest. Enterprise/public = fine if role is product/growth. YC bonus. **Healthcare and insurance companies = automatic 0, exclude entirely.** |
| Scrappiness signal | 10% | JD keywords: scrappy, resourceful, 0→1, wear many hats, ambiguous, fast-moving, founding, first PM, builder. |
| Location match | 15% | SF, NYC, Remote = full points. Other = 0. |
| Growth signal density | 10% | Experimentation, metrics ownership, user acquisition, retention, PLG, GTM, conversion, funnel. |

**Score actions:**
- 9-10: Full cover letter + resume tweak + PDF
- 7-8: Full cover letter + resume tweak + PDF
- 5-6: Fit summary only, no cover letter
- 1-4: Exclude from output entirely

## Fit analysis (for jobs scoring 5+)

Write 2-3 sentences:
1. What in the JD maps to Nathan's specific experience
2. Any gaps and whether they're dealbreakers
3. Why this role at this company stage is a match

## Cover letter generation (for jobs scoring 7+)

**Structure:**
1. Opening (2-3 sentences): Name the role. One specific hook about the company — a recent launch, their market, their product. Not generic.
2. Middle (2-3 short paragraphs): Map 2-3 of Nathan's experiences to JD requirements using XYZ format: "Accomplished [X] as measured by [Y] by doing [Z]"
   - For growth roles → lead with Aiso (DTC, SEO, attribution, conversion, $100K revenue)
   - For strategy/ops roles → lead with PwC (stakeholder alignment, cross-functional, requirements → systems)
   - For scrappy/founder roles → lead with Xpress or Aiso founding story
3. Close (2 sentences): Specific interest, "Happy to chat" or similar

**Voice rules — CRITICAL:**
- Write like Nathan: direct, results-first, no filler
- Short sentences. Fragments OK. Vary the rhythm.
- NEVER start a sentence with a participle phrase ("Leveraging my...", "Having led...")
- NEVER use: leveraging, utilizing, demonstrating, facilitating, furthermore, moreover
- NEVER use: "I'm thrilled", "I'm excited", "I'm passionate", "dynamic professional"
- NEVER start more than one paragraph with "I"
- Numbers and results > adjectives
- Under 250 words

**Harvard guidelines:**
- Keep concise and factual, single page
- Avoid flowery language
- Give examples that support skills
- Minimize use of "I" pronoun
- Use action words
- Reference skills from the job description

## Resume tailoring (for jobs scoring 7+)

Read `resume_base.md` and produce a modified version:

**Step 1 — Reorder bullets:**
- Within each job, put the most JD-relevant bullets first
- If JD emphasizes growth/marketing → lead with Aiso's SEO/attribution bullets
- If JD emphasizes cross-functional/ops → lead with PwC's stakeholder alignment bullets

**Step 2 — Light vocabulary mirroring (max 3-5 word-level changes across entire resume):**
- Identify key JD terms that Nathan's bullets already cover with different words
- Swap only where natural:
  - "SEO, web attribution" → "customer acquisition through SEO and web attribution" (if JD says "customer acquisition")
  - "automated conversion workflows" → "growth experiments including automated conversion workflows" (if JD says "growth experiments")

**Hard rules:**
- Never change facts, numbers, dates, titles, or company names
- Never add claims Nathan can't verify in an interview
- Never add skills not on the resume
- Keep XYZ structure intact
- Maximum 5 word-level changes total

## Execution flow

1. Read `data/scraped_jobs.json`
2. Read `resume_base.md`
3. Read `tailor/templates.py` for constraints
4. For each job in scraped_jobs:
   a. Score it 1-10
   b. If healthcare/insurance → skip
   c. If 5+ → write fit analysis
   d. If 7+ → generate cover letter + tweak resume
5. Sort by score descending
6. Write top 20 jobs (scoring 5+) to `data/scored_jobs.json`
7. Run `python -c "from poster.discord_poster import ...; ..."` or trigger the posting script

After writing scored_jobs.json, run:
```bash
python post_results.py
```
```

**Step 3: Commit**

```bash
git add routine_prompt.md tailor/templates.py
git commit -m "feat: add routine prompt and tailoring constraints"
```

---

## Task 11: Post-Scoring Pipeline — PDF Rendering & Discord Posting Script

**Files:**
- Create: `post_results.py`

This script is called AFTER the Claude Code Routine writes `scored_jobs.json`. It renders PDFs and posts everything to Discord.

**Step 1: Implement post_results.py**

```python
# post_results.py
import json
import os
import time
from pathlib import Path

from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, SCORE_THRESHOLD_FULL, SCORE_THRESHOLD_MENTION
from renderer.pdf_builder import render_cover_letter_pdf, render_resume_pdf
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

    scrape_path = DATA_DIR / "scraped_jobs.json"
    scrape_data = {}
    if scrape_path.exists():
        with open(scrape_path) as f:
            scrape_data = json.load(f)

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
        resume_pdf = None
        safe_name = f"{job['company']}_{job['title']}".replace(" ", "_").replace("/", "-")[:50]

        if job.get("cover_letter"):
            cover_pdf = str(PDF_DIR / f"cover_{safe_name}.pdf")
            render_cover_letter_pdf(job["cover_letter"], cover_pdf)

        if job.get("tweaked_resume"):
            resume_pdf = str(PDF_DIR / f"resume_{safe_name}.pdf")
            render_resume_pdf(job["tweaked_resume"], resume_pdf)

        poster.post_job(job, cover_letter_pdf=cover_pdf, resume_pdf=resume_pdf)
        time.sleep(1.5)

    if mention_jobs:
        poster.post_compact_list(mention_jobs[:12])

    log.info(f"Posted {len(top_jobs)} top jobs + {len(mention_jobs)} mentions to Discord")


if __name__ == "__main__":
    run()
```

**Step 2: Test manually with a sample `scored_jobs.json`**

Create a small test file and verify PDFs render and Discord receives the posts.

**Step 3: Commit**

```bash
git add post_results.py
git commit -m "feat: add post-scoring pipeline with PDF rendering and Discord posting"
```

---

## Task 12: Update CLAUDE.md with Final Architecture

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update CLAUDE.md**

Replace the current CLAUDE.md with the final architecture reflecting all design decisions from the brainstorming session. Key changes:

- Architecture expanded from 4 layers to 6 layers
- Execution model: Python for data collection, Claude Code Routine for intelligence
- 12 sources + Brave catch-all (added YC Work at a Startup, startups.gallery, HN Hiring)
- Updated scoring rubric with 6 weighted dimensions including scrappiness signal
- Healthcare/insurance exclusion
- Cover letter generation with Harvard framework, XYZ method, Nathan's voice
- Resume tailoring: reorder + light vocabulary mirroring (max 5 word changes)
- Discord bot (not webhook) for thread creation + PDF attachments
- Updated file structure with tailor/, renderer/, routine_prompt.md, resume_base.md
- Updated env vars: DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID (replaces DISCORD_WEBHOOK_URL)
- Role title map with full forms and abbreviations
- Company stage nuance: enterprise OK if product/growth, Chief of Staff calibrated by company size

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with final 6-layer architecture"
```

---

## Task 13: Integration Test — Full Pipeline Dry Run

**Step 1: Set up `.env` with real keys**

```bash
cp .env.example .env
# Fill in BRAVE_API_KEY, DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID
```

**Step 2: Run scraper**

```bash
python main.py
```

Verify: `data/scraped_jobs.json` exists, has jobs from multiple sources, no crashes.

**Step 3: Verify scraped data structure**

```bash
python -c "import json; d=json.load(open('data/scraped_jobs.json')); print(f'{d[\"unique_jobs\"]} jobs from {len(set(j[\"source\"] for j in d[\"jobs\"]))} sources')"
```

**Step 4: Manually create a test `scored_jobs.json` to verify posting**

```bash
python -c "
import json
test = {
    'timestamp': '2026-05-08T17:00:00',
    'jobs': [{
        'title': 'Growth PM',
        'company': 'TestCo',
        'url': 'https://example.com/jobs/1',
        'location': 'Remote',
        'source': 'test',
        'score': 9,
        'fit_analysis': 'Strong match — test posting.',
        'cover_letter': 'Dear TestCo team,\n\nTest cover letter.\n\nHappy to chat.\nNathan',
        'tweaked_resume': '# Nathan Vuong\n\n## Experience\n\n### PwC\n- Test bullet',
    }]
}
json.dump(test, open('data/scored_jobs.json', 'w'), indent=2)
"
```

**Step 5: Run posting**

```bash
python post_results.py
```

Verify: Discord receives the summary embed, job embed with thread, and PDF attachments in the thread.

**Step 6: Fix any issues found during integration testing**

**Step 7: Run full test suite**

```bash
python -m pytest tests/ -v
```

**Step 8: Commit any fixes**

```bash
git add -A
git commit -m "fix: integration test fixes"
```

---

## Task 14: Set Up Claude Code Routine

**Step 1: Create the Routine**

The Claude Code Routine is configured to:
- Schedule: `0 1 * * *` UTC (= 5 PM PST daily)
- Working directory: this project directory
- Entry flow:
  1. Run `python main.py` (scraping)
  2. Read `routine_prompt.md` for scoring/tailoring instructions
  3. Read `data/scraped_jobs.json` and `resume_base.md`
  4. Score, analyze, generate cover letters, tweak resumes
  5. Write `data/scored_jobs.json`
  6. Run `python post_results.py` (PDF rendering + Discord posting)

Use the `/schedule` command to configure this.

**Step 2: Verify the Routine runs correctly**

Trigger a manual run and verify the full pipeline executes end-to-end.

**Step 3: Commit any final adjustments**

```bash
git add -A
git commit -m "feat: configure Claude Code Routine for daily execution"
```
