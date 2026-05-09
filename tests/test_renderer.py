import os
from pathlib import Path
from renderer.pdf_builder import render_cover_letter_pdf, render_resume_pdf


def test_render_cover_letter_creates_pdf(tmp_path):
    cover_letter = "Dear Hiring Team,\n\nI am writing about the Growth PM role.\n\nBest,\nNathan"
    output = tmp_path / "cover.pdf"
    render_cover_letter_pdf(cover_letter, str(output))
    assert output.exists()
    assert output.stat().st_size > 0


def test_render_resume_creates_pdf(tmp_path):
    resume_md = "# Nathan Vuong\n\n## Experience\n\n### PwC\n- Did things\n- Did more things"
    output = tmp_path / "resume.pdf"
    render_resume_pdf(resume_md, str(output))
    assert output.exists()
    assert output.stat().st_size > 0
