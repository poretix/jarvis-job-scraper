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
