from unittest.mock import patch, MagicMock
from scraper.yc_startup import YCStartupScraper
from scraper.startups_gallery import StartupsGalleryScraper


def test_yc_startup_handles_no_results():
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "<html><body>No jobs</body></html>"
    with patch("scraper.yc_startup.requests.get", return_value=resp):
        scraper = YCStartupScraper()
        jobs = scraper.extract()
    assert jobs == []


def test_yc_startup_handles_error():
    resp = MagicMock()
    resp.status_code = 500
    with patch("scraper.yc_startup.requests.get", return_value=resp):
        scraper = YCStartupScraper()
        jobs = scraper.extract()
    assert jobs == []


def test_startups_gallery_handles_no_results():
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "<html><body>No jobs</body></html>"
    with patch("scraper.startups_gallery.requests.get", return_value=resp):
        scraper = StartupsGalleryScraper()
        jobs = scraper.extract()
    assert jobs == []


def test_startups_gallery_handles_error():
    resp = MagicMock()
    resp.status_code = 403
    with patch("scraper.startups_gallery.requests.get", return_value=resp):
        scraper = StartupsGalleryScraper()
        jobs = scraper.extract()
    assert jobs == []
