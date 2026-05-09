from utils.deduper import Deduper


def test_deduper_removes_duplicate_urls():
    deduper = Deduper()
    jobs = [
        {"url": "https://a.com/job/1", "title": "PM"},
        {"url": "https://a.com/job/1", "title": "PM duplicate"},
        {"url": "https://b.com/job/2", "title": "Growth"},
    ]
    result = deduper.deduplicate(jobs)
    assert len(result) == 2
    assert result[0]["title"] == "PM"
    assert result[1]["title"] == "Growth"


def test_deduper_handles_empty_list():
    deduper = Deduper()
    assert deduper.deduplicate([]) == []


def test_deduper_normalizes_trailing_slashes():
    deduper = Deduper()
    jobs = [
        {"url": "https://a.com/job/1/", "title": "With slash"},
        {"url": "https://a.com/job/1", "title": "Without slash"},
    ]
    result = deduper.deduplicate(jobs)
    assert len(result) == 1
