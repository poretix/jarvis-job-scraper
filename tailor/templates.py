COVER_LETTER_CONSTRAINTS = {
    "max_words": 250,
    "structure": [
        "Opening: name the role, one specific hook about the company (2-3 sentences)",
        "Middle: 2-3 examples mapping experience to JD using XYZ format (2-3 short paragraphs)",
        "Close: reiterate interest, contact info (2 sentences)",
    ],
    "voice_rules": [
        "Write like Nathan talks: direct, results-first, no filler",
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
    "role_profile_match": {
        "weight": 0.30,
        "description": "Does the JD map to work Nathan has done, including entrepreneurial PM work?",
    },
    "seniority_fit": {
        "weight": 0.20,
        "description": "5+ yr PM title = lower (not disqualifier). Scrappy/0-to-1/startup mentality = boost.",
    },
    "company_stage": {
        "weight": 0.15,
        "description": "Seed-Series B = highest. Enterprise/public OK if product/growth. Healthcare/insurance = excluded.",
    },
    "scrappiness_signal": {
        "weight": 0.10,
        "description": "JD signals builder: scrappy, resourceful, 0-to-1, wear many hats, ambiguous, founding, first PM.",
    },
    "location_match": {
        "weight": 0.15,
        "description": "SF, NYC, Remote = full. Other = 0.",
    },
    "growth_signal_density": {
        "weight": 0.10,
        "description": "Experimentation, metrics ownership, acquisition, retention, PLG, GTM, conversion, funnel.",
    },
}
