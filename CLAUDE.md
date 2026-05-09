# Jarvis — Job Scraper Pipeline

## What this is
Automated daily job scraping pipeline for Nathan Vuong's job search.
Triggers via Claude Code Routine on a cron schedule (5 PM PST daily).
Discovers, scrapes, scores, generates tailored cover letters and resume tweaks,
renders PDFs, and posts everything to Discord.

## Candidate Profile

**Name:** Nathan Vuong
**Location:** Irvine, CA (targeting SF, NYC, Remote roles)
**Background:**
- 3 years PwC Cloud & Digital Consulting (Workday Financials, Fortune 500 clients)
  - Cross-functional alignment, stakeholder management, VOC research, requirements-to-systems
- Co-Founder, Aiso Pickleball ($100K revenue)
  - Product development, DTC brand, SEO, web attribution, conversion optimization, influencer marketing
- Founder, Xpress Distribution ($175K revenue, 53% ROI, 40-user inventory system)
  - Demand evaluation, automation, proxy infrastructure, Python tooling
- Technical: Python, SQL, HTML/CSS/JS, Figma, Jira, REST APIs, Claude Code
- Education: UCSB Economics & Accounting, 3.95 GPA, AWS Cloud Practitioner

**Target Roles (priority order):**
1. Growth: Growth Manager, Growth Associate, Growth Analyst, Growth Lead, Growth PM,
   Growth Product Manager, Growth Marketing Manager, Head of Growth, Lifecycle Marketing Manager
2. Product: Product Manager, Associate PM, Founding PM, First PM, Product Lead,
   Product Growth Manager, Product Operations Manager
3. Strategy & Ops: Chief of Staff (seed/Series A), Strategy & Operations,
   Business Operations, RevOps, GTM Operations, Strategic Initiatives
4. Adjacent: Partnerships Manager, Business Development, Product Marketing Manager,
   Marketplace Manager, GTM Manager, Solutions Manager, Community Manager

**Target companies:** Seed through Series B startups, YC-backed preferred. Open to larger
tech companies for direct Growth/Product roles. **Healthcare and insurance excluded.**

**Target locations:** San Francisco, New York City, Remote

## Architecture

Six-layer pipeline split between Python (data collection, PDF rendering, Discord posting)
and Claude Code Routine (scoring, fit analysis, cover letter generation, resume tailoring).

```
Claude Code Routine triggers daily at 5 PM PST
|
|- 1. DISCOVER  (Python)  -- Brave Search API finds job board URLs
|- 2. EXTRACT   (Python)  -- HTTP scrapes 12 sources
|- 3. SCORE     (Claude)  -- Reads scraped jobs + resume, scores 1-10
|- 4. TAILOR    (Claude)  -- For 7+: cover letter + resume tweak
|- 5. RENDER    (Python)  -- Converts materials to PDF
|- 6. POST      (Python)  -- Discord embeds + threads with PDF attachments
```

### Layer 1: Discovery — Brave Search API
- Dynamically discovers companies and job board URLs
- Queries structured around role titles + startup signals
- Returns Greenhouse/Lever/Ashby URLs for extraction layer
- Brave API free tier = 2,000 queries/month, budgeted at ~30 queries/run

### Layer 2: Extraction — Direct HTTP (12 sources)
| Source | Method | Tier |
|--------|--------|------|
| Greenhouse | JSON API | 1 |
| Lever | JSON API | 1 |
| Ashby | JSON API | 1 |
| YC Work at a Startup | HTML scrape | 1 |
| startups.gallery | HTML scrape | 1 |
| RemoteOK | JSON API | 2 |
| Himalayas | JSON API | 2 |
| Built In SF/NYC | HTML scrape | 2 |
| HN Who is Hiring | HN API | 3 |
| Wellfound | Via Brave index | 3 |
| Lenny's Job Board | Via Brave index | 3 |
| Reforge Job Board | Via Brave index | 3 |

No browser, no Playwright — pure requests + BeautifulSoup/JSON parsing.
Deduplicates by URL across all sources within a run.

### Layer 3: Scoring — Claude Code Routine
Scores each listing 1-10 using 6 weighted dimensions (see routine_prompt.md):
- Role-profile match (30%) — does the JD map to Nathan's actual experience?
- Seniority fit (20%) — 5+ yr PM title = lower, scrappy signals = boost
- Company stage (15%) — seed-Series B highest, enterprise OK if product/growth, healthcare/insurance excluded
- Scrappiness signal (10%) — JD mentions builder/founding/0-to-1
- Location match (15%) — SF, NYC, Remote = full
- Growth signal density (10%) — experimentation, metrics, PLG, GTM

Actions: 7+ = full cover letter + resume tweak. 5-6 = fit summary only. 1-4 = excluded.

### Layer 4: Tailoring — Claude Code Routine
Cover letters: Harvard framework + Google XYZ method, Nathan's direct voice.
Resume tweaks: Reorder bullets + max 3-5 word-level vocabulary mirrors.
See routine_prompt.md for full rules, voice constraints, and anti-AI-detection patterns.

### Layer 5: Rendering — PDF Generation
fpdf2 converts cover letters and tweaked resumes to clean PDFs.
Unicode characters sanitized to latin-1 (en dashes, smart quotes, bullets).

### Layer 6: Output — Discord Bot
Discord bot token (not webhook) for thread creation + PDF attachments.
- Daily summary embed with source stats and error reporting
- Per-job embeds (7+) with thread auto-replies containing cover_letter.pdf + resume.pdf
- Compact list for 5-6 scored jobs
- No-matches fallback with near-miss info

## File Structure
```
jarvis/
├── CLAUDE.md                  ← Architecture context for Claude Code sessions
├── resume_base.md             ← Nathan's structured resume (source of truth)
├── routine_prompt.md          ← Instructions for Claude Code Routine (scoring + tailoring)
├── .env                       ← API keys (never commit)
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py                    ← Scraping orchestrator (discovery + extraction + dedup)
├── post_results.py            ← Post-scoring pipeline (PDF render + Discord post)
├── config.py                  ← Role targets, search queries, source URLs, thresholds
├── scraper/
│   ├── brave_search.py        ← Brave Search API discovery
│   ├── greenhouse.py          ← Greenhouse JSON API
│   ├── lever.py               ← Lever JSON API
│   ├── ashby.py               ← Ashby JSON API
│   ├── yc_startup.py          ← YC Work at a Startup scraper
│   ├── startups_gallery.py    ← startups.gallery scraper
│   ├── remoteok.py            ← RemoteOK public JSON API
│   ├── himalayas.py           ← Himalayas scraper
│   ├── builtin.py             ← Built In SF/NYC scraper
│   └── hn_hiring.py           ← HN "Who is Hiring" thread parser
├── tailor/
│   └── templates.py           ← Scoring dimensions, voice rules, cover letter constraints
├── renderer/
│   └── pdf_builder.py         ← Markdown-to-PDF for cover letters and resumes
├── poster/
│   └── discord_poster.py      ← Discord bot posting with threads + file attachments
├── utils/
│   ├── deduper.py             ← URL deduplication within a run
│   └── logger.py              ← Structured logging
├── data/                      ← Runtime data (gitignored)
│   ├── scraped_jobs.json      ← Raw scrape output
│   ├── scored_jobs.json       ← Claude's scored + analyzed output
│   └── pdfs/                  ← Generated PDFs per job
└── tests/
    ├── test_utils.py
    ├── test_brave.py
    ├── test_ats.py
    ├── test_public_apis.py
    ├── test_specialty.py
    ├── test_renderer.py
    └── test_discord.py
```

## Environment Variables
```
BRAVE_API_KEY=           # Brave Search API (free tier, 2000 queries/month)
DISCORD_BOT_TOKEN=       # Discord bot token
DISCORD_CHANNEL_ID=      # Target channel ID for job postings
```

## Key Decisions & Constraints
- No Playwright or browser automation — cloud Routine has no browser
- No LinkedIn scraping — IP rate limiting risk on cloud infrastructure
- No separate Claude API key — Routine does AI work using subscription
- Wellfound excluded from direct scraping — auth walls. Covered via Brave index
- Healthcare and insurance companies excluded entirely from scoring
- Brave API free tier = 2,000 queries/month. Budget ~30 queries per run
- Target runtime under 3 minutes per full pipeline run
- All errors caught per-source; one source failing must not abort pipeline
- Errors reported in Discord summary footer
- Cover letters follow Harvard framework + Google XYZ method
- Resume tweaks limited to reorder + max 5 word-level vocabulary mirrors
- Anti-AI-detection: no participle phrases, no filler enthusiasm, Nathan's direct voice
- Discord uses bot token for thread creation (not webhook)

## Running Locally
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys
python main.py         # runs scraping only
# Then Claude scores + tailors, writing scored_jobs.json
python post_results.py # renders PDFs and posts to Discord
```

## Routine Execution Flow
1. Routine triggers at 5 PM PST (0 1 * * * UTC)
2. Runs `python main.py` (scraping -> data/scraped_jobs.json)
3. Claude reads routine_prompt.md, scraped_jobs.json, resume_base.md
4. Claude scores, writes fit analysis, generates cover letters, tweaks resumes
5. Claude writes data/scored_jobs.json
6. Runs `python post_results.py` (PDFs + Discord posting)


<claude-mem-context>
# Recent Activity

<!-- This section is auto-generated by claude-mem. Edit content outside the tags. -->

*No recent activity*
</claude-mem-context>