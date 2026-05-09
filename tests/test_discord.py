from unittest.mock import patch, MagicMock
from poster.discord_poster import DiscordPoster


def _mock_post_response(message_id="111"):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"id": message_id}
    return resp


def test_post_summary_sends_embed():
    with patch("poster.discord_poster.requests.post", return_value=_mock_post_response()) as mock:
        poster = DiscordPoster(bot_token="test", channel_id="123")
        poster.post_summary(
            total_scraped=147,
            unique=89,
            top_matches=8,
            worth_a_look=12,
            errors=[],
            elapsed=134.2,
        )
    assert mock.called


def test_post_job_creates_thread():
    responses = [
        _mock_post_response("msg-1"),  # main message
        _mock_post_response("thread-1"),  # thread creation
        _mock_post_response(),  # file upload 1
        _mock_post_response(),  # file upload 2
    ]
    with patch("poster.discord_poster.requests.post", side_effect=responses):
        poster = DiscordPoster(bot_token="test", channel_id="123")
        poster.post_job(
            job={
                "title": "Growth PM",
                "company": "Ramp",
                "url": "https://ramp.com/jobs/1",
                "location": "NYC",
                "score": 9,
                "fit_analysis": "Strong match.",
            },
            cover_letter_pdf="/tmp/nonexistent_cover.pdf",
            resume_pdf="/tmp/nonexistent_resume.pdf",
        )
