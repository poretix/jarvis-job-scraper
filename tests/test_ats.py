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
