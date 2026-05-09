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
