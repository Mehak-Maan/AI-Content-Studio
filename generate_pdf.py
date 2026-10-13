"""
Generate a professional PDF from the AI Content Studio README.md
Uses ReportLab for PDF generation.
"""
import re
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Preformatted
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ─── Paths ──────────────────────────────────────────────────────────────────
README_PATH = os.path.join(os.path.dirname(__file__), "README.md")
OUTPUT_PDF  = os.path.join(os.path.dirname(__file__), "AI_Content_Studio_Documentation.pdf")

# ─── Color Palette ───────────────────────────────────────────────────────────
C_BG        = colors.HexColor("#0F172A")   # dark navy
C_ACCENT    = colors.HexColor("#6366F1")   # indigo
C_ACCENT2   = colors.HexColor("#22D3EE")   # cyan
C_GREEN     = colors.HexColor("#22C55E")
C_YELLOW    = colors.HexColor("#FBBF24")
C_TEXT      = colors.HexColor("#1E293B")   # dark text
C_MUTED     = colors.HexColor("#475569")
C_CODE_BG   = colors.HexColor("#1E293B")
C_CODE_TEXT = colors.HexColor("#E2E8F0")
C_TABLE_HDR = colors.HexColor("#4338CA")
C_TABLE_ALT = colors.HexColor("#EEF2FF")
C_WHITE     = colors.white
C_BORDER    = colors.HexColor("#CBD5E1")

# ─── Styles ──────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)

style_h1 = make_style("H1",
    fontSize=28, leading=34, textColor=C_ACCENT,
    fontName="Helvetica-Bold", spaceAfter=8, spaceBefore=16,
    alignment=TA_CENTER)

style_h2 = make_style("H2",
    fontSize=17, leading=22, textColor=C_ACCENT,
    fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=18,
    borderPad=4)

style_h3 = make_style("H3",
    fontSize=13, leading=18, textColor=C_TEXT,
    fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=12)

style_h4 = make_style("H4",
    fontSize=11, leading=15, textColor=C_MUTED,
    fontName="Helvetica-Bold", spaceAfter=3, spaceBefore=8)

style_body = make_style("Body",
    fontSize=10, leading=16, textColor=C_TEXT,
    fontName="Helvetica", spaceAfter=4, alignment=TA_JUSTIFY)

style_bullet = make_style("Bullet",
    fontSize=10, leading=15, textColor=C_TEXT,
    fontName="Helvetica", leftIndent=18, spaceAfter=2,
    bulletIndent=6, bulletFontName="Helvetica")

style_code = make_style("Code",
    fontSize=8.5, leading=13, textColor=C_CODE_TEXT,
    fontName="Courier", leftIndent=10, rightIndent=10,
    backColor=C_CODE_BG, spaceBefore=4, spaceAfter=4,
    borderColor=C_ACCENT, borderWidth=0)

style_subtitle = make_style("Subtitle",
    fontSize=13, leading=18, textColor=C_MUTED,
    fontName="Helvetica", spaceAfter=6, alignment=TA_CENTER)

style_badge = make_style("Badge",
    fontSize=9, leading=13, textColor=C_MUTED,
    fontName="Helvetica", spaceAfter=2, alignment=TA_CENTER)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def clean_inline(text):
    """Convert simple markdown inline to ReportLab XML."""
    # Escape XML special chars first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold-italic ***
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold **
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italic *
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Inline code `
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" color="#6366F1">\1</font>', text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'<u>\1</u>', text)
    # Remove badges like [![...](...)](...)
    text = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', text)
    return text.strip()

def build_table(lines):
    """Parse markdown table lines into a ReportLab Table."""
    rows = []
    for line in lines:
        if re.match(r'^\|[-| :]+\|$', line.strip()):
            continue  # separator row
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)

    if not rows:
        return None

    col_count = max(len(r) for r in rows)
    # Pad rows
    rows = [r + [''] * (col_count - len(r)) for r in rows]

    table_data = []
    for i, row in enumerate(rows):
        if i == 0:
            table_data.append([
                Paragraph(f"<b>{clean_inline(c)}</b>", make_style(f"th{i}",
                    fontSize=9, leading=13, textColor=C_WHITE,
                    fontName="Helvetica-Bold", alignment=TA_CENTER))
                for c in row
            ])
        else:
            table_data.append([
                Paragraph(clean_inline(c), make_style(f"td{i}",
                    fontSize=9, leading=13, textColor=C_TEXT,
                    fontName="Helvetica"))
                for c in row
            ])

    col_width = (A4[0] - 4*cm) / col_count
    t = Table(table_data, colWidths=[col_width]*col_count, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  C_TABLE_HDR),
        ('TEXTCOLOR',     (0,0), (-1,0),  C_WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [C_WHITE, C_TABLE_ALT]),
        ('GRID',          (0,0), (-1,-1), 0.4, C_BORDER),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('ROUNDEDCORNERS',(0,0), (-1,-1), [3,3,3,3]),
    ]))
    return t

def on_first_page(canvas, doc):
    """Draw cover background on page 1."""
    canvas.saveState()
    # Dark gradient-like header band
    canvas.setFillColor(C_BG)
    canvas.rect(0, A4[1]-8*cm, A4[0], 8*cm, fill=1, stroke=0)
    # Accent bar
    canvas.setFillColor(C_ACCENT)
    canvas.rect(0, A4[1]-8*cm, A4[0], 0.3*cm, fill=1, stroke=0)
    canvas.restoreState()

def on_later_pages(canvas, doc):
    """Header/footer for pages 2+."""
    canvas.saveState()
    # Top bar
    canvas.setFillColor(C_ACCENT)
    canvas.rect(0, A4[1]-0.8*cm, A4[0], 0.8*cm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(C_WHITE)
    canvas.drawString(2*cm, A4[1]-0.55*cm, "AI Content Studio — Documentation")
    canvas.drawRightString(A4[0]-2*cm, A4[1]-0.55*cm, f"Page {doc.page}")
    # Bottom bar
    canvas.setFillColor(C_BORDER)
    canvas.rect(0, 0, A4[0], 0.6*cm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(C_MUTED)
    canvas.drawCentredString(A4[0]/2, 0.2*cm, "github.com/Mehak-Maan/AI-Content-Studio")
    canvas.restoreState()

# ─── Main Builder ─────────────────────────────────────────────────────────────

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        title="AI Content Studio Documentation",
        author="Mehak Maan",
        subject="Multi-Agent AI Video Generation Pipeline"
    )

    with open(README_PATH, encoding="utf-8") as f:
        lines = f.readlines()

    story = []

    # ── Cover block ──────────────────────────────────────────
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("🎬 AI Content Studio", style_h1))
    story.append(Paragraph("Autonomous Multi-Agent AI Video Generator", style_subtitle))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="80%", thickness=2, color=C_ACCENT, spaceAfter=10, spaceBefore=10))
    story.append(Paragraph(
        "A complete pipeline that converts a text prompt into a fully edited video — "
        "with AI scenes, neural voice-over, background music, and burned subtitles.",
        make_style("CoverDesc", fontSize=11, leading=17, textColor=C_MUTED,
                   fontName="Helvetica", alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 0.5*cm))

    # Metadata row
    meta_data = [[
        Paragraph("<b>GitHub</b><br/>github.com/Mehak-Maan/<br/>AI-Content-Studio",
                  make_style("m1", fontSize=9, leading=13, textColor=C_TEXT,
                             fontName="Helvetica", alignment=TA_CENTER)),
        Paragraph("<b>Backend</b><br/>Python 3.12<br/>FastAPI + LangGraph",
                  make_style("m2", fontSize=9, leading=13, textColor=C_TEXT,
                             fontName="Helvetica", alignment=TA_CENTER)),
        Paragraph("<b>Frontend</b><br/>React 18 + Vite<br/>Tailwind CSS",
                  make_style("m3", fontSize=9, leading=13, textColor=C_TEXT,
                             fontName="Helvetica", alignment=TA_CENTER)),
        Paragraph("<b>AI Video</b><br/>MagicHour.ai<br/>Text-to-Video",
                  make_style("m4", fontSize=9, leading=13, textColor=C_TEXT,
                             fontName="Helvetica", alignment=TA_CENTER)),
    ]]
    meta_table = Table(meta_data, colWidths=[(A4[0]-4*cm)/4]*4)
    meta_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), C_TABLE_ALT),
        ('BOX',          (0,0), (-1,-1), 1, C_ACCENT),
        ('INNERGRID',    (0,0), (-1,-1), 0.5, C_BORDER),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 10),
        ('BOTTOMPADDING',(0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # ── Parse Markdown ────────────────────────────────────────
    i = 0
    in_code_block = False
    code_lines = []
    in_table = False
    table_lines = []

    while i < len(lines):
        line = lines[i].rstrip('\n')

        # Code block start/end
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lines = []
            else:
                in_code_block = False
                code_text = '\n'.join(code_lines)
                # Limit code block length and line length for readability
                if len(code_lines) > 30:
                    code_text = '\n'.join(code_lines[:30]) + '\n... (truncated for brevity)'
                # Wrap lines longer than 80 chars
                wrapped = []
                for cl in code_text.splitlines():
                    if len(cl) > 80:
                        wrapped.append(cl[:80] + ' ...')
                    else:
                        wrapped.append(cl)
                code_text = '\n'.join(wrapped)
                story.append(Spacer(1, 4))
                # Draw code box
                box_data = [[Preformatted(code_text, style_code)]]
                code_table = Table(box_data, colWidths=[A4[0]-4*cm])
                code_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), C_CODE_BG),
                    ('BOX',        (0,0), (-1,-1), 1, C_ACCENT),
                    ('LEFTPADDING',(0,0), (-1,-1), 10),
                    ('RIGHTPADDING',(0,0),(-1,-1), 10),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING',(0,0),(-1,-1), 8),
                ]))
                story.append(code_table)
                story.append(Spacer(1, 4))
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table detection
        if line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line.strip())
            i += 1
            continue
        else:
            if in_table:
                in_table = False
                t = build_table(table_lines)
                if t:
                    story.append(Spacer(1, 6))
                    story.append(t)
                    story.append(Spacer(1, 6))
                table_lines = []

        # Skip badge lines
        if line.strip().startswith('[!['):
            i += 1
            continue

        # Headings
        h_match = re.match(r'^(#{1,4})\s+(.*)', line)
        if h_match:
            level = len(h_match.group(1))
            text  = clean_inline(h_match.group(2))
            if level == 1:
                story.append(Spacer(1, 0.3*cm))
                story.append(HRFlowable(width="100%", thickness=1, color=C_ACCENT,
                                        spaceAfter=4, spaceBefore=4))
                story.append(Paragraph(text, style_h2))
                story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER,
                                        spaceAfter=4, spaceBefore=2))
            elif level == 2:
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph(text, style_h2))
                story.append(HRFlowable(width="50%", thickness=0.5, color=C_ACCENT,
                                        spaceAfter=3, spaceBefore=0))
            elif level == 3:
                story.append(Paragraph(text, style_h3))
            else:
                story.append(Paragraph(text, style_h4))
            i += 1
            continue

        # Mermaid / ASCII diagram — treat as code
        if line.strip().startswith('```mermaid') or (
            i > 0 and lines[i-1].strip().startswith('```mermaid')):
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}$', line.strip()):
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=C_BORDER, spaceAfter=6, spaceBefore=6))
            i += 1
            continue

        # Bullet / list
        bullet_match = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if bullet_match:
            indent = len(bullet_match.group(1))
            text   = clean_inline(bullet_match.group(2))
            left   = 18 + indent * 10
            story.append(Paragraph(
                f"• {text}",
                make_style(f"B{indent}", fontSize=10, leading=15,
                           textColor=C_TEXT, fontName="Helvetica",
                           leftIndent=left, spaceAfter=2)
            ))
            i += 1
            continue

        # Numbered list
        num_match = re.match(r'^\s*\d+\.\s+(.*)', line)
        if num_match:
            text = clean_inline(num_match.group(1))
            story.append(Paragraph(
                f"&#x25B6; {text}",
                make_style("NL", fontSize=10, leading=15, textColor=C_TEXT,
                           fontName="Helvetica", leftIndent=18, spaceAfter=2)
            ))
            i += 1
            continue

        # Blockquote
        if line.strip().startswith('>'):
            text = clean_inline(line.strip().lstrip('>').strip())
            box  = Table([[Paragraph(f"<i>{text}</i>",
                           make_style("BQ", fontSize=9.5, leading=14,
                                      textColor=C_MUTED, fontName="Helvetica-Oblique"))]],
                         colWidths=[A4[0]-4*cm])
            box.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,-1), C_TABLE_ALT),
                ('LEFTPADDING',   (0,0), (-1,-1), 14),
                ('RIGHTPADDING',  (0,0), (-1,-1), 10),
                ('TOPPADDING',    (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LINEBEFORE',    (0,0), (-1,-1), 3, C_ACCENT),
            ]))
            story.append(box)
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Empty line
        if not line.strip():
            story.append(Spacer(1, 5))
            i += 1
            continue

        # Regular paragraph
        text = clean_inline(line)
        if text:
            story.append(Paragraph(text, style_body))
        i += 1

    # flush trailing table
    if in_table and table_lines:
        t = build_table(table_lines)
        if t:
            story.append(t)

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f"PDF created successfully: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
