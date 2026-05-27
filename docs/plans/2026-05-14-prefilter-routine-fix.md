# Pre-Filter + Routine Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a Python pre-scoring step so the Claude Code Routine only processes ~30 high-signal jobs instead of ~1,400, then update the routine config so it actually works end-to-end.

**Architecture:** `main.py` scrapes 1,400 jobs → NEW `prescorer.py` applies keyword/location/seniority scoring to narrow to top 30 with truncated descriptions (~16K tokens) → routine reads small `filtered_jobs.json` + resume, scores with Claude, writes cover letters → `post_results.py` posts to Discord.

**Tech Stack:** Python, regex, JSON, Claude Code Routines API (RemoteTrigger)

---

### Task 1: Create the Python pre-scorer

**Files:**
- Create: `prescorer.py`
- Reference: `config.py` (reuse LOCATIONS, EXCLUDED_INDUSTRIES, ROLE_TITLES)

**Step 1: Write the failing test**

Create `tests/test_prescorer.py`:

```python
import json
from prescorer import prescore_jobs


def test_prescore_filters_excluded_industries():
    jobs = [
        {"title": "Product Manager", "company": "HealthCo", "location": "NYC", "description": "healthcare insurance company", "url": "http://a", "source": "greenhouse"},
        {"title": "Product Manager", "company": "StartupX", "location": "San Francisco", "description": "Series A startup building growth tools", "url": "http://b", "source": "greenhouse"},
    ]
    result = prescore_jobs(jobs)
    assert len(result) == 1
    assert result[0]["company"] == "StartupX"


def test_prescore_scores_location():
    jobs = [
        {"title": "Product Manager", "company": "A", "location": "San Francisco", "description": "startup", "url": "http://a", "source": "gh"},
        {"title": "Product Manager", "company": "B", "location": "Austin, TX", "description": "startup", "url": "http://b", "source": "gh"},
    ]
    result = prescore_jobs(jobs)
    assert result[0]["company"] == "A"
    assert result[0]["prescore"] > result[1]["prescore"]


def test_prescore_penalizes_senior_titles():
    jobs = [
        {"title": "Product Manager", "company": "A", "location": "NYC", "description": "startup growth", "url": "http://a", "source": "gh"},
        {"title": "Senior Staff Product Manager", "company": "B", "location": "NYC", "description": "startup growth", "url": "http://b", "source": "gh"},
    ]
    result = prescore_jobs(jobs)
    assert result[0]["company"] == "A"


def test_prescore_boosts_growth_signals():
    jobs = [
        {"title": "Product Manager", "company": "A", "location": "Remote", "description": "growth experimentation PLG funnel metrics", "url": "http://a", "source": "gh"},
        {"title": "Product Manager", "company": "B", "location": "Remote", "description": "manage team and roadmap", "url": "http://b", "source": "gh"},
    ]
    result = prescore_jobs(jobs)
    assert result[0]["company"] == "A"


def test_prescore_truncates_description():
    long_desc = "x" * 10000
    jobs = [
        {"title": "PM", "company": "A", "location": "NYC", "description": long_desc, "url": "http://a", "source": "gh"},
    ]
    result = prescore_jobs(jobs)
    assert len(result[0]["description"]) <= 2000


def test_prescore_caps_at_max_results():
    jobs = [
        {"title": "PM", "company": f"Co{i}", "location": "NYC", "description": "startup growth", "url": f"http://{i}", "source": "gh"}
        for i in range(100)
    ]
    result = prescore_jobs(jobs, max_results=30)
    assert len(result) <= 30


def test_prescore_preserves_required_fields():
    jobs = [
        {"title": "Growth PM", "company": "X", "location": "SF", "description": "growth startup", "url": "http://x", "source": "lever"},
    ]
    result = prescore_jobs(jobs)
    assert all(k in result[0] for k in ("title", "company", "location", "url", "source", "description", "prescore"))
```

**Step 2: Run test to verify it fails**

Run: `cd "/Users/nathanvuong/Vibe Coding/Job Scraper" && source venv/bin/activate && python -m pytest tests/test_prescorer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'prescorer'`

**Step 3: Write the implementation**

Create `prescorer.py`:

```python
import json
import re
from pathlib import Path
from config import EXCLUDED_INDUSTRIES

_LOC_PATTERN = re.compile(r"(san francisco|\bsf\b|new york|\bnyc\b|\bremote\b)", re.I)
_SCRAPPY_PATTERN = re.compile(
    r"(scrappy|0.to.1|zero.to.one|founding|first pm|wear many hats"
    r"|ambiguous|fast.moving|builder|early.stage|\bseed\b|series [ab]\b)", re.I
)
_GROWTH_PATTERN = re.compile(
    r"(growth|experimentation|acquisition|retention|\bplg\b|product.led"
    r"|\bgtm\b|conversion|funnel|metrics|a/b test|lifecycle)", re.I
)
_EXCLUDE_PATTERN = re.compile(
    "|".join(re.escape(ind) for ind in EXCLUDED_INDUSTRIES), re.I
)
_SENIOR_PATTERN = re.compile(
    r"\b(senior|staff|principal|director|\bvp\b|vice president)\b", re.I
)

DESC_TRUNCATE = 2000
DEFAULT_MAX = 30


def prescore_jobs(jobs, max_results=DEFAULT_MAX):
    scored = []
    for job in jobs:
        desc = job.get("description", "")
        company = job.get("company", "")
        title = job.get("title", "")
        location = job.get("location", "")

        if _EXCLUDE_PATTERN.search(desc[:500]) or _EXCLUDE_PATTERN.search(company):
            continue

        score = 0
        if _LOC_PATTERN.search(location):
            score += 3
        score += min(len(_SCRAPPY_PATTERN.findall(desc)), 3)
        score += min(len(_GROWTH_PATTERN.findall(desc)), 3)
        if _SENIOR_PATTERN.search(title):
            score -= 2

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
```

**Step 4: Run tests to verify they pass**

Run: `cd "/Users/nathanvuong/Vibe Coding/Job Scraper" && source venv/bin/activate && python -m pytest tests/test_prescorer.py -v`
Expected: All 7 tests PASS

**Step 5: Commit**

```bash
git add prescorer.py tests/test_prescorer.py
git commit -m "feat: add Python pre-scorer to filter jobs before Claude scoring"
```

---

### Task 2: Wire pre-scorer into main.py

**Files:**
- Modify: `main.py` (add prescorer call at end of `run_scrape()`)

**Step 1: Add prescorer call**

At the end of `main.py`, after `run_scrape()` returns, call `prescorer.run()`:

```python
# Add import at top
from prescorer import run as run_prescore

# In __main__ block, change to:
if __name__ == "__main__":
    run_scrape()
    run_prescore()
```

**Step 2: Test locally**

Run: `cd "/Users/nathanvuong/Vibe Coding/Job Scraper" && source venv/bin/activate && python main.py`
Expected: Scraping completes, then prints "Pre-scored 1381 -> 30 jobs -> data/filtered_jobs.json"

Verify: `python -c "import json; d=json.load(open('data/filtered_jobs.json')); print(f'Jobs: {len(d[\"jobs\"])}, file size: {len(json.dumps(d))} chars')"`
Expected: Jobs: 30, file size ~65K chars

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: wire pre-scorer into scraping pipeline"
```

---

### Task 3: Update post_results.py to read filtered_jobs.json for scrape stats

**Files:**
- Modify: `post_results.py` (change scrape_path fallback to read filtered_jobs.json)

**Step 1: Update scrape data source**

In `post_results.py`, change the scrape stats source to prefer `filtered_jobs.json` (since the routine writes `scored_jobs.json` based on filtered input):

```python
# Change this block (around line 38-42):
    scrape_path = DATA_DIR / "scraped_jobs.json"
    scrape_data = {}
    if scrape_path.exists():
        with open(scrape_path) as f:
            scrape_data = json.load(f)

# To:
    scrape_data = {}
    for fname in ["filtered_jobs.json", "scraped_jobs.json"]:
        spath = DATA_DIR / fname
        if spath.exists():
            with open(spath) as f:
                scrape_data = json.load(f)
            break
```

**Step 2: Commit**

```bash
git add post_results.py
git commit -m "fix: read filtered_jobs.json for scrape stats in Discord summary"
```

---

### Task 4: Update the routine prompt to read filtered_jobs.json

**Files:**
- Modify: `routine_prompt.md`

**Step 1: Update file references**

Change all references from `data/scraped_jobs.json` to `data/filtered_jobs.json` in routine_prompt.md.

Specifically in "Your Inputs" section (line 8):
```
1. `data/filtered_jobs.json` — pre-filtered job listings (~30 top candidates)
```

And in "Execution Flow" section (line 145):
```
1. Read `data/filtered_jobs.json`
```

**Step 2: Commit**

```bash
git add routine_prompt.md
git commit -m "fix: routine reads filtered_jobs.json instead of full scraped data"
```

---

### Task 5: Update the routine config via RemoteTrigger API

**Files:**
- No code files — uses RemoteTrigger API to update the cloud routine

**Step 1: Update the routine prompt**

The routine prompt in the trigger config needs these changes:
1. Step 2 output: `python main.py` now also produces `data/filtered_jobs.json`
2. Step 3: Read `data/filtered_jobs.json` instead of `data/scraped_jobs.json`
3. Add cron schedule: `0 1 * * *` (daily at 5 PM PST / 1 AM UTC)
4. Remove `run_once_at`

Use `RemoteTrigger` with action `update` and trigger_id `trig_01FoYnM2ka52i98HrMwVGJbf`:

```json
{
  "enabled": true,
  "cron_expression": "0 1 * * *",
  "run_once_at": null,
  "job_config": {
    "ccr": {
      "environment_id": "env_01RMyhBQRXDSLKS8Dz2YMXQ8",
      "events": [{
        "data": {
          "message": {
            "content": "<UPDATED PROMPT WITH filtered_jobs.json REFERENCES>",
            "role": "user"
          },
          "type": "user",
          "uuid": "b4e2f1a8-7c3d-4e5b-9a6f-1d2e3c4b5a68"
        }
      }],
      "session_context": {
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
        "model": "claude-sonnet-4-6",
        "sources": [{"git_repository": {"url": "https://github.com/poretix/jarvis-job-scraper"}}]
      }
    }
  }
}
```

**Step 2: Verify the update**

Use `RemoteTrigger` with action `get` to confirm:
- `enabled: true`
- `cron_expression: "0 1 * * *"`
- Prompt references `filtered_jobs.json`

---

### Task 6: Push to GitHub and trigger test run

**Step 1: Push all commits**

```bash
git push origin main
```

**Step 2: Trigger a one-time test run**

Use `RemoteTrigger` with action `run` to fire immediately.

**Step 3: Monitor Discord**

Watch `#job-search` for results within ~5-10 minutes. If results appear, the pipeline works.

**Step 4: If no results, check routine status**

Use `RemoteTrigger` with action `get` to check `last_fired_at` and `ended_reason`.
