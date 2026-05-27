# Jarvis Routine — Scoring & Tailoring Instructions

You are running as a Claude Code Routine for Jarvis, Nathan Vuong's job scraper pipeline.
The scraping phase has already run. Your job: score jobs, analyze fit, generate cover letters, tweak resumes.

## Your Inputs

1. `data/filtered_jobs.json` — pre-filtered top ~30 job listings from the scraping phase
2. `resume_base.md` — Nathan's base resume (source of truth)
3. `tailor/templates.py` — constraints for cover letters, resume tweaks, and scoring

## Your Outputs

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
      "resume_tweaks": [
        {
          "section": "Aiso Pickleball",
          "original": "full original bullet from resume_base.md",
          "replacement": "full replacement bullet with JD vocabulary mirrored"
        }
      ]
    }
  ]
}
```

## Candidate Profile

Nathan Vuong — Irvine, CA, targeting SF/NYC/Remote.

Background:
- 3 years PwC Cloud & Digital Consulting (Workday Financials, Fortune 500 clients, cross-functional alignment, stakeholder management, VOC research, requirements-to-systems)
- Co-Founder, Aiso Pickleball ($100K revenue, DTC brand, SEO, web attribution, conversion optimization, influencer marketing, community research, product development)
- Founder, Xpress Distribution ($175K revenue at 53% ROI, demand evaluation, automation, proxy infrastructure, inventory system for 40 users)
- Technical: Python, SQL, HTML/CSS/JS, Figma, Jira, REST APIs, Claude Code
- Education: UCSB Economics & Accounting, 3.95 GPA, AWS Certified Cloud Practitioner

Key strengths: entrepreneurial builder who ships revenue-generating products from scratch, cross-functional alignment from consulting, data-driven decision making, scrappy and resourceful.

## Scoring Rubric (1-10)

Score each job using these weighted dimensions:

| Dimension | Weight | Evaluation |
|-----------|--------|------------|
| Role-profile match | 30% | Does the JD map to Growth/Product/Strategy/Ops work Nathan has actually done — including entrepreneurial PM work at Aiso and Xpress? |
| Seniority fit | 20% | 5+ yr PM title at BigCo = lower score (not disqualifier). "Scrappy", "0-to-1", "startup mentality", "entrepreneurial" = signal boost. Nathan has ~3 years professional + 5 years entrepreneurial. |
| Company stage | 15% | Seed-Series B = highest. Enterprise/public = fine if role is product/growth. YC bonus. **Healthcare and insurance companies = automatic 0, exclude entirely.** |
| Scrappiness signal | 10% | JD keywords: scrappy, resourceful, 0-to-1, wear many hats, ambiguous, fast-moving, founding, first PM, builder. |
| Location match | 15% | SF, NYC, Remote = full points. Other = 0. |
| Growth signal density | 10% | Experimentation, metrics ownership, user acquisition, retention, PLG, GTM, conversion, funnel. |

**Score actions:**
- 9-10: Full cover letter + resume tweak
- 7-8: Full cover letter + resume tweak
- 5-6: Fit summary only, no cover letter
- 1-4: Exclude from output entirely

## Fit Analysis (for jobs scoring 5+)

Write 2-3 sentences:
1. What in the JD maps to Nathan's specific experience
2. Any gaps and whether they're dealbreakers
3. Why this role at this company stage is a match

Example:
> "Strong match: JD emphasizes growth experimentation and conversion optimization — maps directly to Aiso's DTC brand work (SEO, attribution, automated conversion workflows). They want someone who's 'built 0-to-1' which aligns with founding experience. Minor gap: JD mentions SQL for analytics, which Nathan has but isn't highlighted on resume. Series A, YC W24. 9/10."

## Cover Letter Generation (for jobs scoring 7+)

**Structure (Harvard framework):**
1. Opening (2-3 sentences): Name the role. One specific hook about the company — a recent launch, their market, their product. Not generic.
2. Middle (2-3 short paragraphs): Map 2-3 of Nathan's experiences to JD requirements using XYZ format: "Accomplished [X] as measured by [Y] by doing [Z]"
   - For growth roles: lead with Aiso (DTC, SEO, attribution, conversion, $100K revenue)
   - For strategy/ops roles: lead with PwC (stakeholder alignment, cross-functional, requirements-to-systems)
   - For scrappy/founder roles: lead with Xpress or Aiso founding story
3. Close (2 sentences): Specific interest, "Happy to chat" or similar

**Voice rules — CRITICAL:**
- Write like Nathan: direct, results-first, no filler
- Short sentences. Fragments OK. Vary the rhythm.
- NEVER start a sentence with a participle phrase ("Leveraging my...", "Having led...")
- NEVER use: leveraging, utilizing, demonstrating, facilitating, furthermore, moreover
- NEVER use: "I'm thrilled", "I'm excited", "I'm passionate", "dynamic professional"
- NEVER use: "I look forward to the opportunity to discuss"
- NEVER start more than one paragraph with "I"
- Numbers and results beat adjectives about yourself
- Under 250 words total
- The reader should be able to tell a specific person wrote this, not a template

**Anti-AI-detection rules:**
- Vary sentence structure: mix short declarative with longer compound
- No filler enthusiasm
- Use active voice throughout
- Close with "Happy to chat" not formal sign-offs

## Resume Tailoring (for jobs scoring 7+)

Read `resume_base.md` and produce a structured list of bullet swaps — NOT a full resume.
Nathan keeps a master formatted resume and will copy-paste your suggested changes.

**Output format — `resume_tweaks` array:**
Each entry is one bullet change. Provide the FULL original bullet and the FULL replacement bullet so Nathan can copy-paste directly.
```json
{
  "section": "Aiso Pickleball",
  "original": "Developed a direct to consumer brand through SEO, web attribution analysis, automated conversion workflows, and post purchase surveys to optimize acquisition channels and inform iterative product improvements",
  "replacement": "Developed a direct to consumer brand through growth experiments including SEO, web attribution analysis, and conversion optimization to optimize acquisition channels and inform iterative product improvements"
}
```

- `section`: the company/section name exactly as it appears in resume_base.md
- `original`: the FULL bullet text from resume_base.md (exact match)
- `replacement`: the FULL revised bullet with vocabulary mirroring applied

**Rules for vocabulary mirroring (max 3-5 changes across entire resume):**
- Identify key JD terms that Nathan's bullets already cover with different words
- Swap only where natural — change a few words, not the structure
- Each entry = one bullet swap. Only include bullets that actually change.

**Hard rules:**
- Never change facts, numbers, dates, titles, or company names
- Never add claims Nathan can't verify in an interview
- Never add skills not on the resume
- Keep XYZ structure intact
- Maximum 5 bullet changes total across the entire resume
- Only include bullets that need changes — skip everything else

## Execution Flow

1. Read `data/filtered_jobs.json`
2. Read `resume_base.md`
3. For each job in filtered_jobs:
   a. Score it 1-10
   b. If healthcare/insurance company: skip entirely
   c. If score 5+: write fit analysis
   d. If score 7+: generate cover letter + tweak resume
4. Sort by score descending
5. Write top 20 jobs (scoring 5+) to `data/scored_jobs.json`
6. Run: `python post_results.py`
