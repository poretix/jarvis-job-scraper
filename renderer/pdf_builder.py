from pathlib import Path
from fpdf import FPDF

FONTS_DIR = Path(__file__).parent / "fonts"

UNICODE_REPLACEMENTS = {
    "'": "'",
    "'": "'",
    "“": '"',
    "”": '"',
    "…": "...",
}

BULLET = "●"


def _sanitize(text):
    for char, replacement in UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    return text


class _BasePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(25, 20, 25)
        self.set_font("Helvetica", size=11)


def render_cover_letter_pdf(text, output_path):
    pdf = _BasePDF()
    pdf.set_font("Helvetica", size=11)
    for line in _sanitize(text).split("\n"):
        if line.strip() == "":
            pdf.ln(6)
        else:
            pdf.multi_cell(0, 6, line.strip(), new_x="LMARGIN", new_y="NEXT")
    pdf.output(output_path)


def _parse_resume_sections(markdown_text):
    lines = markdown_text.split("\n")
    sections = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("# ") and not line.startswith("## "):
            name = line[2:]
            contact = ""
            j = i + 1
            while j < len(lines):
                candidate = lines[j].strip()
                if candidate:
                    if not candidate.startswith("#"):
                        contact = candidate
                        j += 1
                    break
                j += 1
            sections.append({"type": "header", "name": name, "contact": contact})
            i = j
            continue
        if line.startswith("## "):
            section_title = line[3:]
            content = []
            i += 1
            while i < len(lines):
                l = lines[i].strip()
                if l.startswith("## "):
                    break
                if l:
                    content.append(l)
                elif content:
                    content.append("")
                i += 1
            sections.append({"type": "section", "title": section_title, "content": content})
            continue
        i += 1
    return sections


def _parse_experience_block(content_lines):
    blocks = []
    i = 0
    while i < len(content_lines):
        line = content_lines[i]
        if line.startswith("### "):
            company = line[4:]
            title_line = content_lines[i + 1] if i + 1 < len(content_lines) else ""
            date_loc_line = content_lines[i + 2] if i + 2 < len(content_lines) else ""
            title = title_line.strip("*") if title_line.startswith("**") else title_line
            location, dates = "", ""
            if "|" in date_loc_line:
                parts = date_loc_line.split("|")
                dates = parts[0].strip()
                location = parts[1].strip()
            else:
                dates = date_loc_line

            bullets = []
            j = i + 3
            while j < len(content_lines):
                bl = content_lines[j]
                if bl.startswith("### "):
                    break
                if bl.startswith("- "):
                    bullets.append(bl[2:])
                j += 1
            blocks.append({
                "company": company, "title": title,
                "location": location, "dates": dates, "bullets": bullets,
            })
            i = j
            continue
        i += 1
    return blocks


def _add_tnr_fonts(pdf):
    pdf.add_font("TNR", "", str(FONTS_DIR / "Times New Roman.ttf"))
    pdf.add_font("TNR", "B", str(FONTS_DIR / "Times New Roman Bold.ttf"))
    pdf.add_font("TNR", "I", str(FONTS_DIR / "Times New Roman Italic.ttf"))
    pdf.add_font("TNR", "BI", str(FONTS_DIR / "Times New Roman Bold Italic.ttf"))


CONTACT_LINKS = {
    "nvuong3.professional@gmail.com": "mailto:nvuong3.professional@gmail.com",
    "LinkedIn": "https://www.linkedin.com/in/nathanvuong3",
    "Portfolio": "https://nathanvuong.com",
}


def _render_contact_line(pdf, contact, W, FONT):
    parts = contact.split(" | ")
    sep = " | "
    sep_w = pdf.get_string_width(sep)
    part_widths = [pdf.get_string_width(p.strip()) for p in parts]
    total_w = sum(part_widths) + sep_w * (len(parts) - 1)
    x_start = pdf.l_margin + (W - total_w) / 2
    pdf.set_x(x_start)

    for idx, part in enumerate(parts):
        p = part.strip()
        pw = part_widths[idx]
        if p in CONTACT_LINKS:
            pdf.set_text_color(17, 85, 204)
            pdf.set_font(FONT, "U", pdf.font_size_pt)
            pdf.cell(pw, 4.5, p, link=CONTACT_LINKS[p], new_x="RIGHT", new_y="TOP")
            pdf.set_font(FONT, "", pdf.font_size_pt)
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.cell(pw, 4.5, p, new_x="RIGHT", new_y="TOP")
        if idx < len(parts) - 1:
            pdf.cell(sep_w, 4.5, sep, new_x="RIGHT", new_y="TOP")
    pdf.ln(4.5)


def render_resume_pdf(markdown_text, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_margins(19, 14, 19)
    W = pdf.w - 38

    _add_tnr_fonts(pdf)
    FONT = "TNR"
    sections = _parse_resume_sections(markdown_text)

    LH = 4.8
    BULLET_INDENT = 7
    BULLET_COL_W = 5.5

    is_first_section = True
    for sec in sections:
        if sec["type"] == "header":
            pdf.set_font(FONT, "B", 16)
            pdf.cell(0, 7, sec["name"], align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(FONT, size=9)
            _render_contact_line(pdf, sec["contact"], W, FONT)
            continue

        if is_first_section:
            pdf.ln(2)
            is_first_section = False
        else:
            pdf.ln(3)

        pdf.set_font(FONT, "B", 12.5)
        pdf.cell(0, 6.5, sec["title"], new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.5)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + W, pdf.get_y())
        pdf.ln(1.5)

        if sec["title"] in ("Work Experience", "Education", "Relevant Experience"):
            blocks = _parse_experience_block(sec["content"])
            for bi, block in enumerate(blocks):
                pdf.set_font(FONT, "B", 10)
                pdf.cell(W * 0.6, LH, block["company"])
                pdf.cell(W * 0.4, LH, block["location"], align="R",
                         new_x="LMARGIN", new_y="NEXT")

                pdf.set_font(FONT, "I", 10)
                pdf.cell(W * 0.6, LH, block["title"])
                pdf.cell(W * 0.4, LH, block["dates"], align="R",
                         new_x="LMARGIN", new_y="NEXT")

                for bullet in block["bullets"]:
                    pdf.set_font(FONT, "", 10)
                    pdf.set_x(pdf.l_margin + BULLET_INDENT)
                    pdf.cell(BULLET_COL_W, LH, BULLET, new_x="RIGHT", new_y="TOP")
                    pdf.multi_cell(W - BULLET_INDENT - BULLET_COL_W, LH, bullet,
                                   new_x="LMARGIN", new_y="NEXT")
                if bi < len(blocks) - 1:
                    pdf.ln(1)
        else:
            pdf.set_font(FONT, "", 10)
            for line in sec["content"]:
                if not line:
                    pdf.ln(1)
                elif line.startswith("- "):
                    text = line[2:]
                    pdf.set_x(pdf.l_margin + BULLET_INDENT)
                    pdf.cell(BULLET_COL_W, LH, BULLET, new_x="RIGHT", new_y="TOP")
                    pdf.multi_cell(W - BULLET_INDENT - BULLET_COL_W, LH, text,
                                   new_x="LMARGIN", new_y="NEXT")
                else:
                    pdf.multi_cell(W, LH, line, new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)
