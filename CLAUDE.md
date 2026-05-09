# Jarvis — Job Scraper Pipeline

## What this is
Automated daily job scraping pipeline for Nathan Vuong's job search.
Triggers via Claude Code Routine on a cron schedule (5 PM PST daily).
Discovers, scrapes, scores, and posts curated job listings to Discord.

## Candidate Profile

**Name:** Nathan Vuong  
**Location:** Irvine, CA (targeting SF, NYC, Remote roles)  
**Background:**
- 3 years PwC Cloud & Digital Consulting (Workday Financials, Fortune 500 clients)
  - Cross-functional alignment, stakeholder management, VOC research, requirements → systems
- Co-Founder, Aiso Pickleball ($100K revenue)
  - Product development, DTC brand, SEO, web attribution, conversion optimization, influencer marketing
- Founder, Xpress Distribution ($175K ticket arbitrage, sneaker resale, 40-user inventory system)
  - Demand evaluation, automation, proxy infrastructure, Python tooling
- Technical: Python, SQL, HTML/CSS/JS, Figma, Jira, REST APIs, Claude Code

**Target Roles (priority order):**
1. Growth (Growth Associate, Growth Analyst, Growth Manager, Growth PM, Head of Growth)
2. Product (PM, Associate PM, Founding PM, Product Growth, Product Operations)
3. Strategy & Ops (Biz Ops, Strategy & Ops, RevOps, GTM Ops, Chief of Staff)
4. Adjacent (Partnerships, GTM, Product Marketing with growth component)

**Target companies:** Seed through Series B startups, YC-backed preferred. Open to larger
tech companies for direct Growth/Product roles.

**Target locations:** San Francisco, New York City, Remote

## Architecture

### Discovery Layer — Brave Search API
- Dynamically discovers companies and job board URLs
- Queries structured around role titles + startup signals
- Returns Greenhouse/Lever/Ashby URLs for extraction layer
- Also surfaces Wellfound, Lenny's, and other boards via index
- API key stored in .env as BRAVE_API_KEY

### Extraction Layer — Direct HTTP
- Hits discovered Greenhouse/Lever/Ashby board URLs directly
- Also hits known public APIs: RemoteOK, Himalayas, Built In SF/NYC
- No browser, no Playwright — pure requests + BeautifulSoup/JSON parsing
- Deduplicates by URL across all sources within a run

### Scoring Layer
- Scores each listing 1-10 against candidate profile (see scoring.py)
- Posts only listings scoring 6+ to Discord
- Max 20 posts per run (top by score)

### Output Layer — Discord Webhook
- Webhook URL stored in .env as DISCORD_WEBHOOK_URL
- Rich embed format per listing (see discord_poster.py)
- Batch posts up to 10 embeds per request
- Posts a "no matches" summary if zero listings score 6+

## File Structure
```
jarvis/
├── CLAUDE.md              ← You are here
├── README.md
├── .env                   ← API keys (never commit)
├── .env.example           ← Committed template
├── .gitignore
├── requirements.txt
├── main.py                ← Entry point, orchestrates full pipeline
├── config.py              ← Role targets, scoring weights, search queries
├── scraper/
│   ├── __init__.py
│   ├── brave_search.py    ← Brave Search API discovery
│   ├── greenhouse.py      ← Direct HTTP extraction for Greenhouse boards
│   ├── lever.py           ← Direct HTTP extraction for Lever boards
│   ├── remoteok.py        ← RemoteOK public JSON API
│   ├── himalayas.py       ← Himalayas HTTP scrape
│   └── builtin.py         ← Built In SF/NYC HTTP scrape
├── scorer/
│   ├── __init__.py
│   └── scoring.py         ← Scoring logic against candidate profile
├── poster/
│   ├── __init__.py
│   └── discord_poster.py  ← Discord webhook formatting and posting
├── utils/
│   ├── __init__.py
│   ├── deduper.py         ← URL deduplication within a run
│   └── logger.py          ← Structured logging
└── tests/
    ├── test_brave.py
    ├── test_scoring.py
    └── test_discord.py
```

## Environment Variables
```
BRAVE_API_KEY=           # Brave Search API key
DISCORD_WEBHOOK_URL=     # Discord webhook for job postings
```

## Key Decisions & Constraints
- No Playwright or browser automation — cloud Routine has no browser
- No LinkedIn scraping — IP rate limiting risk on cloud infrastructure
- Wellfound excluded from direct scraping — auth walls. Covered partially via Brave index
- Brave API free tier = 2,000 queries/month. Budget ~60/day across all queries
- Target runtime under 3 minutes per full pipeline run
- All errors should be caught per-source; one source failing must not abort the pipeline
- Log errors to Discord footer so failures are visible without checking logs manually

## Scoring Criteria (summary — see scorer/scoring.py for full logic)
HIGH (7-10): Seed/Series A/B startup, founding PM or first PM, growth experiments/metrics
ownership, biz ops/strategy at startup, generalist PM, YC-backed, SF/NYC/Remote,
no strict 3+ yr PM title requirement
LOW (1-4): Enterprise, 5+ yr PM title required, deep technical PM, irrelevant domain

## Running Locally
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in keys
python main.py
```

## Routine Trigger (Claude Code Cloud)
- Schedule: 0 17 * * * PST (= 0 1 * * * UTC)
- Entry point: python main.py


<claude-mem-context>
# Recent Activity

<!-- This section is auto-generated by claude-mem. Edit content outside the tags. -->

*No recent activity*
</claude-mem-context>