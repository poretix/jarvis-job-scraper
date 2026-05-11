import os
import requests
from utils.logger import get_logger

log = get_logger("discord")

BASE_URL = "https://discord.com/api/v10"


class DiscordPoster:
    def __init__(self, bot_token, channel_id):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.headers = {
            "Authorization": f"Bot {bot_token}",
            "User-Agent": "Jarvis/1.0",
        }

    def post_summary(self, total_scraped, unique, top_matches, worth_a_look, errors, elapsed):
        error_text = ""
        if errors:
            error_lines = [f"- {e}" for e in errors[:5]]
            error_text = "\n".join(error_lines)

        embed = {
            "title": "Jarvis Daily Report",
            "color": 0x5865F2,
            "fields": [
                {"name": "Jobs Found", "value": str(total_scraped), "inline": True},
                {"name": "After Dedup", "value": str(unique), "inline": True},
                {"name": "Top Matches (7+)", "value": str(top_matches), "inline": True},
                {"name": "Worth a Look (5-6)", "value": str(worth_a_look), "inline": True},
                {"name": "Runtime", "value": f"{elapsed:.0f}s", "inline": True},
            ],
        }
        if error_text:
            embed["footer"] = {"text": f"Errors:\n{error_text}"}

        self._send_message({"embeds": [embed]})

    def post_job(self, job, cover_letter_pdf=None):
        score = job["score"]
        color = 0x57F287 if score >= 9 else 0xFEE75C if score >= 7 else 0x99AAB5

        embed = {
            "title": f"{'🟢' if score >= 9 else '🟡' if score >= 7 else '⚪'} {score}/10 — {job['title']} @ {job['company']}",
            "url": job["url"],
            "color": color,
            "fields": [
                {"name": "Location", "value": job.get("location", "N/A"), "inline": True},
                {"name": "Fit Analysis", "value": job.get("fit_analysis", "")[:1024]},
            ],
        }

        msg = self._send_message({"embeds": [embed]})
        if not msg:
            return

        message_id = msg.get("id")
        if not message_id:
            return

        thread = self._create_thread(message_id, f"{job['title']} @ {job['company']}")
        if not thread:
            return

        thread_id = thread.get("id")
        if cover_letter_pdf and os.path.exists(cover_letter_pdf):
            self._upload_file(thread_id, cover_letter_pdf, "cover_letter.pdf")

        resume_tweaks = job.get("resume_tweaks")
        if resume_tweaks:
            self._post_resume_tweaks(thread_id, resume_tweaks)

    def post_compact_list(self, jobs):
        lines = []
        for job in jobs:
            score = job["score"]
            lines.append(f"**{score}/10** — [{job['title']} @ {job['company']}]({job['url']})")
            if job.get("fit_analysis"):
                lines.append(f"  _{job['fit_analysis'][:100]}_")
            lines.append("")

        embed = {
            "title": "Worth a Look (5-6)",
            "description": "\n".join(lines)[:4096],
            "color": 0x99AAB5,
        }
        self._send_message({"embeds": [embed]})

    def post_no_matches(self, total_scanned, near_miss=None):
        desc = f"No matches today. {total_scanned} jobs scanned, none scored above 5."
        if near_miss:
            desc += f"\nTop near-miss: {near_miss['title']} @ {near_miss['company']} ({near_miss['score']}/10)"
        embed = {"title": "No Matches", "description": desc, "color": 0xED4245}
        self._send_message({"embeds": [embed]})

    def _post_resume_tweaks(self, thread_id, tweaks):
        lines = ["**Resume Tweaks for This Role:**\n"]
        for tweak in tweaks:
            section = tweak.get("section", "")
            lines.append(f"__**{section}**__")
            lines.append(f"Find:\n```{tweak['original']}```")
            lines.append(f"Replace with:\n```{tweak['replacement']}```")
            lines.append("")

        text = "\n".join(lines)
        if len(text) > 1900:
            chunks = [text[i:i+1900] for i in range(0, len(text), 1900)]
            for chunk in chunks:
                self._send_thread_message(thread_id, chunk)
        else:
            self._send_thread_message(thread_id, text)

    def _send_thread_message(self, thread_id, content):
        try:
            resp = requests.post(
                f"{BASE_URL}/channels/{thread_id}/messages",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"content": content},
                timeout=10,
            )
            if resp.status_code not in (200, 201):
                log.error(f"Thread message failed: {resp.status_code}")
        except Exception as e:
            log.error(f"Thread message error: {e}")

    def _send_message(self, payload):
        try:
            resp = requests.post(
                f"{BASE_URL}/channels/{self.channel_id}/messages",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )
            if resp.status_code != 200:
                log.error(f"Discord send failed: {resp.status_code} {resp.text[:200]}")
                return None
            return resp.json()
        except Exception as e:
            log.error(f"Discord send error: {e}")
            return None

    def _create_thread(self, message_id, name):
        try:
            resp = requests.post(
                f"{BASE_URL}/channels/{self.channel_id}/messages/{message_id}/threads",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"name": name[:100], "auto_archive_duration": 1440},
                timeout=10,
            )
            if resp.status_code not in (200, 201):
                log.error(f"Thread creation failed: {resp.status_code}")
                return None
            return resp.json()
        except Exception as e:
            log.error(f"Thread creation error: {e}")
            return None

    def _upload_file(self, channel_id, file_path, filename):
        try:
            with open(file_path, "rb") as f:
                resp = requests.post(
                    f"{BASE_URL}/channels/{channel_id}/messages",
                    headers={"Authorization": f"Bot {self.bot_token}"},
                    files={"file": (filename, f, "application/pdf")},
                    timeout=15,
                )
            if resp.status_code not in (200, 201):
                log.error(f"File upload failed: {resp.status_code}")
        except Exception as e:
            log.error(f"File upload error: {e}")
