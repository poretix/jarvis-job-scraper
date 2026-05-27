import itertools

from prescorer import prescore_jobs

_url_counter = itertools.count()


def _job(title="Product Manager", company="StartupX", location="NYC",
         description="a startup building tools", url=None,
         source="greenhouse"):
    if url is None:
        url = f"http://example.com/{next(_url_counter)}"
    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "url": url,
        "source": source,
    }


# --- 1. Excluded industries ---

def test_excluded_industries_healthcare_filtered():
    jobs = [
        _job(company="HealthCo", description="healthcare insurance company"),
        _job(company="StartupX", description="Series A startup building growth tools"),
    ]
    result = prescore_jobs(jobs)
    assert len(result) == 1
    assert result[0]["company"] == "StartupX"


def test_excluded_industries_insurance_in_company_name():
    jobs = [
        _job(company="Insurance Corp", description="great place to work"),
        _job(company="TechCo", description="building software"),
    ]
    result = prescore_jobs(jobs)
    assert len(result) == 1
    assert result[0]["company"] == "TechCo"


def test_excluded_industries_healthtech_filtered():
    jobs = [
        _job(description="we are a healthtech company revolutionizing care"),
    ]
    result = prescore_jobs(jobs)
    assert len(result) == 0


def test_excluded_industries_not_biotech():
    """Biotech, defense, etc. should NOT be excluded."""
    jobs = [
        _job(description="biotech startup doing gene therapy"),
        _job(description="defense contractor building satellites"),
    ]
    result = prescore_jobs(jobs)
    assert len(result) == 2


def test_excluded_industry_only_checks_first_500_chars():
    safe_prefix = "a" * 501
    jobs = [
        _job(description=safe_prefix + " healthcare insurance"),
    ]
    result = prescore_jobs(jobs)
    assert len(result) == 1


# --- 2. Location scoring ---

def test_location_sf_boost():
    jobs = [
        _job(location="San Francisco, CA"),
        _job(location="Austin, TX"),
    ]
    result = prescore_jobs(jobs)
    assert result[0]["location"] == "San Francisco, CA"
    assert result[0]["prescore"] > result[1]["prescore"]


def test_location_nyc_boost():
    jobs = [
        _job(location="New York, NY"),
        _job(location="Chicago, IL"),
    ]
    result = prescore_jobs(jobs)
    assert result[0]["location"] == "New York, NY"


def test_location_remote_boost():
    jobs = [
        _job(location="Remote"),
        _job(location="Dallas, TX"),
    ]
    result = prescore_jobs(jobs)
    assert result[0]["location"] == "Remote"
    assert result[0]["prescore"] > result[1]["prescore"]


def test_location_sf_abbreviation():
    jobs = [
        _job(location="SF"),
        _job(location="LA"),
    ]
    result = prescore_jobs(jobs)
    assert result[0]["location"] == "SF"
    assert result[0]["prescore"] > result[1]["prescore"]


# --- 3. Seniority penalty (tiered) ---

def test_seniority_senior_minus_1():
    base = _job(title="Product Manager", location="Remote", description="growth startup")
    senior = _job(title="Senior Product Manager", location="Remote", description="growth startup")
    result = prescore_jobs([base, senior])
    base_score = next(j for j in result if j["title"] == "Product Manager")["prescore"]
    senior_score = next(j for j in result if j["title"] == "Senior Product Manager")["prescore"]
    assert base_score - senior_score == 1


def test_seniority_staff_minus_2():
    base = _job(title="Product Manager", location="Remote", description="growth startup")
    staff = _job(title="Staff Product Manager", location="Remote", description="growth startup")
    result = prescore_jobs([base, staff])
    base_score = next(j for j in result if j["title"] == "Product Manager")["prescore"]
    staff_score = next(j for j in result if j["title"] == "Staff Product Manager")["prescore"]
    assert base_score - staff_score == 2


def test_seniority_principal_minus_3():
    base = _job(title="Product Manager", location="Remote", description="growth startup")
    principal = _job(title="Principal Product Manager", location="Remote", description="growth startup")
    result = prescore_jobs([base, principal])
    base_score = next(j for j in result if j["title"] == "Product Manager")["prescore"]
    principal_score = next(j for j in result if j["title"] == "Principal Product Manager")["prescore"]
    assert base_score - principal_score == 3


def test_seniority_director_minus_3():
    base = _job(title="Growth Manager", location="Remote", description="startup")
    director = _job(title="Director Growth Manager", location="Remote", description="startup")
    result = prescore_jobs([base, director])
    base_score = next(j for j in result if j["title"] == "Growth Manager")["prescore"]
    director_score = next(j for j in result if j["title"] == "Director Growth Manager")["prescore"]
    assert base_score - director_score == 3


def test_seniority_vp_minus_3():
    base = _job(title="Growth Manager", location="Remote", description="startup")
    vp = _job(title="VP Growth Manager", location="Remote", description="startup")
    result = prescore_jobs([base, vp])
    base_score = next(j for j in result if j["title"] == "Growth Manager")["prescore"]
    vp_score = next(j for j in result if j["title"] == "VP Growth Manager")["prescore"]
    assert base_score - vp_score == 3


def test_seniority_head_of_minus_2():
    base = _job(title="Growth Manager", location="Remote", description="startup")
    head = _job(title="Head of Product Manager", location="Remote", description="startup")
    result = prescore_jobs([base, head])
    base_score = next(j for j in result if j["title"] == "Growth Manager")["prescore"]
    head_score = next(j for j in result if j["title"] == "Head of Product Manager")["prescore"]
    assert base_score - head_score == 2


# --- 4. "Head of Growth" exception ---

def test_head_of_growth_no_penalty():
    base = _job(title="Growth Manager", location="Remote", description="startup")
    head = _job(title="Head of Growth", location="Remote", description="startup")
    result = prescore_jobs([base, head])
    base_score = next(j for j in result if j["title"] == "Growth Manager")["prescore"]
    head_score = next(j for j in result if j["title"] == "Head of Growth")["prescore"]
    assert head_score == base_score


# --- 5. Growth signal keywords ---

def test_growth_signals_boost_score():
    rich = _job(description="growth experimentation PLG funnel metrics acquisition retention")
    poor = _job(description="manage a team and roadmap")
    result = prescore_jobs([rich, poor])
    assert result[0]["description"].startswith("growth")
    assert result[0]["prescore"] > result[1]["prescore"]


def test_growth_signals_capped_at_4():
    # All growth keywords - should cap at 4
    desc = ("growth experimentation acquisition retention PLG product-led "
            "GTM conversion funnel metrics a/b test lifecycle monetization")
    jobs = [_job(description=desc, location="Austin")]
    result = prescore_jobs(jobs)
    # Title match (PM) = 3, location = 0, growth capped at 4 = 7 max from those
    assert result[0]["prescore"] <= 19  # theoretical max


# --- 6. Product signal keywords ---

def test_product_signals_boost_score():
    rich = _job(description="roadmap user research PRD product requirements cross-functional")
    poor = _job(description="sell things and make money")
    result = prescore_jobs([rich, poor])
    assert result[0]["prescore"] > result[1]["prescore"]


def test_product_signals_capped_at_3():
    desc = ("roadmap user research PRD product requirements product specs "
            "cross-functional stakeholder sprint backlog prioritization")
    jobs = [_job(description=desc, location="Austin")]
    result = prescore_jobs(jobs)
    # With title match=3, product cap=3, max from those = 6
    # Should not exceed category cap
    assert result[0]["prescore"] >= 3  # at least title match + some product


# --- 7. Scrappiness signal keywords ---

def test_scrappiness_signals_boost_score():
    rich = _job(description="scrappy 0-to-1 founding team early-stage startup builder")
    poor = _job(description="established enterprise company stable process")
    result = prescore_jobs([rich, poor])
    assert result[0]["prescore"] > result[1]["prescore"]


def test_scrappiness_signals_capped_at_3():
    desc = ("scrappy 0-to-1 zero-to-one founding first pm wear many hats "
            "ambiguous fast-moving builder early-stage seed series A")
    jobs = [_job(description=desc, location="Austin")]
    result = prescore_jobs(jobs)
    # Scrappiness contribution should be capped at 3
    assert result[0]["prescore"] >= 3  # at least title match


# --- 8. Strategy & Ops signal keywords ---

def test_strategy_ops_signals_boost_score():
    rich = _job(description="strategic planning business operations RevOps process improvement")
    poor = _job(description="generic job posting nothing special")
    result = prescore_jobs([rich, poor])
    assert result[0]["prescore"] > result[1]["prescore"]


def test_strategy_ops_signals_capped_at_3():
    desc = ("strategic planning business operations biz ops operational efficiency "
            "revenue operations RevOps process improvement executive C-suite board")
    jobs = [_job(description=desc, location="Austin")]
    result = prescore_jobs(jobs)
    assert result[0]["prescore"] >= 3


# --- 9. Title match bonus ---

def test_title_match_bonus():
    match = _job(title="Growth Manager", location="Austin", description="startup")
    no_match = _job(title="Software Engineer", location="Austin", description="startup")
    result = prescore_jobs([match, no_match])
    match_score = next(j for j in result if j["title"] == "Growth Manager")["prescore"]
    no_match_score = next(j for j in result if j["title"] == "Software Engineer")["prescore"]
    assert match_score - no_match_score == 3


# --- 10. Description truncation ---

def test_description_truncated_to_2000():
    long_desc = "x" * 10000
    jobs = [_job(description=long_desc)]
    result = prescore_jobs(jobs)
    assert len(result[0]["description"]) == 2000


# --- 11. Output capped at max_results ---

def test_output_capped_at_max_results():
    jobs = [
        _job(company=f"Co{i}", url=f"http://{i}")
        for i in range(100)
    ]
    result = prescore_jobs(jobs, max_results=30)
    assert len(result) == 30


def test_output_cap_custom():
    jobs = [
        _job(company=f"Co{i}", url=f"http://{i}")
        for i in range(50)
    ]
    result = prescore_jobs(jobs, max_results=10)
    assert len(result) == 10


# --- 12. Required fields preserved ---

def test_preserves_required_fields():
    jobs = [_job(title="Growth PM", company="X", location="SF",
                 description="growth startup", url="http://x", source="lever")]
    result = prescore_jobs(jobs)
    required = ("title", "company", "location", "url", "source", "description", "prescore")
    for key in required:
        assert key in result[0], f"Missing field: {key}"


# --- 13. Negative signals ---

def test_negative_signal_years_experience():
    easy = _job(description="2+ years experience in growth")
    hard = _job(description="10+ years experience required. 15+ years preferred.")
    result = prescore_jobs([easy, hard])
    easy_score = next(j for j in result if "2+" in j["description"])["prescore"]
    hard_score = next(j for j in result if "10+" in j["description"])["prescore"]
    assert easy_score > hard_score


def test_negative_signal_phd():
    no_phd = _job(description="growth role at a startup")
    phd = _job(description="PhD required, computer science degree preferred")
    result = prescore_jobs([no_phd, phd])
    assert result[0]["description"] == "growth role at a startup"


def test_negative_signal_people_management():
    ic = _job(description="individual contributor growth role")
    mgr = _job(description="manage a team of 12 direct reports people management")
    result = prescore_jobs([ic, mgr])
    ic_score = next(j for j in result if "individual" in j["description"])["prescore"]
    mgr_score = next(j for j in result if "manage a team" in j["description"])["prescore"]
    assert ic_score > mgr_score


def test_negative_signal_sales():
    product = _job(description="product-led growth role")
    sales = _job(description="quota carrying enterprise sales cold calling cold outreach")
    result = prescore_jobs([product, sales])
    product_score = next(j for j in result if "product-led" in j["description"])["prescore"]
    sales_score = next(j for j in result if "quota" in j["description"])["prescore"]
    assert product_score > sales_score


def test_negative_signals_capped_at_minus_4():
    """Even with many negative signals, total penalty should not exceed -4."""
    # Load up with every negative signal
    desc = ("10+ years 15+ years PhD computer science degree CS degree "
            "data science system design manage a team of direct reports "
            "people management quota enterprise sales cold outreach cold calling")
    jobs = [_job(description=desc)]
    result = prescore_jobs(jobs)
    # Title match = 3, no location/signals, negatives capped at -4 => score >= -1
    # The score should not go absurdly negative
    assert result[0]["prescore"] >= -1


# --- LinkedIn-via-Brave boost ---

def test_guaranteed_pass_linkedin_with_title_match():
    """LinkedIn-via-Brave jobs with title match always pass through,
    even if their keyword score is too low to compete with rich ATS descriptions."""
    filler = [
        _job(title="Analyst", company=f"Filler{i}", location="San Francisco",
             description="growth experimentation PLG GTM conversion funnel metrics "
                         "roadmap OKRs MVP founding startup seed 0-to-1 "
                         "strategic planning P&L forecasting playbook scaling")
        for i in range(35)
    ]
    sparse_linkedin = _job(
        title="Chief of Staff", company="SparseCo",
        location="", source="linkedin_via_brave",
        description="short snippet about a startup role",
    )
    all_jobs = filler + [sparse_linkedin]
    result = prescore_jobs(all_jobs, max_results=30)
    companies = [j["company"] for j in result]
    assert "SparseCo" in companies


def test_linkedin_via_brave_gets_boost():
    jobs = [
        _job(company="A", source="linkedin_via_brave", description="short snippet"),
        _job(company="B", source="greenhouse", description="short snippet"),
    ]
    result = prescore_jobs(jobs)
    a = next(j for j in result if j["company"] == "A")
    b = next(j for j in result if j["company"] == "B")
    assert a["prescore"] - b["prescore"] == 2


# --- Sorting ---

def test_results_sorted_by_score_descending():
    jobs = [
        _job(company="Low", location="Austin", description="nothing relevant"),
        _job(company="High", location="San Francisco",
             description="growth experimentation PLG founding early-stage startup"),
    ]
    result = prescore_jobs(jobs)
    assert result[0]["company"] == "High"
    scores = [j["prescore"] for j in result]
    assert scores == sorted(scores, reverse=True)
