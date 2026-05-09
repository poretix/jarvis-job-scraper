from fpdf import FPDF


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
    for line in text.split("\n"):
        if line.strip() == "":
            pdf.ln(6)
        else:
            pdf.multi_cell(0, 6, line.strip(), new_x="LMARGIN", new_y="NEXT")
    pdf.output(output_path)


def render_resume_pdf(markdown_text, output_path):
    pdf = _BasePDF()
    for line in markdown_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            pdf.ln(4)
        elif stripped.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, stripped[2:], new_x="LMARGIN", new_y="NEXT")
        elif stripped.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, stripped[3:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(200, 200, 200)
            pdf.line(25, pdf.get_y(), 185, pdf.get_y())
            pdf.ln(2)
        elif stripped.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, stripped[4:], new_x="LMARGIN", new_y="NEXT")
        elif stripped.startswith("**") and stripped.endswith("**"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, stripped[2:-2], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=11)
        elif stripped.startswith("- "):
            pdf.set_font("Helvetica", size=10)
            pdf.set_x(pdf.l_margin + 5)
            pdf.multi_cell(0, 5, f"- {stripped[2:]}", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 6, stripped, new_x="LMARGIN", new_y="NEXT")
    pdf.output(output_path)
