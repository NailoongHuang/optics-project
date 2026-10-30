"""Build the plain-language Chinese report from report.md and local figures.

Run with a Python environment containing reportlab and pillow. Chinese TrueType
fonts are located on Windows by default; pass --font-dir on another system.
"""
from pathlib import Path
import argparse
import html
import json
import re

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import textsplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus import paragraph as paragraph_layout

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
INK = colors.HexColor("#193D4C")
MUTED = colors.HexColor("#566873")
RULE = colors.HexColor("#D7E1E5")
PALE = colors.HexColor("#F1F6F7")


def register_fonts(font_dir):
    # Extend the renderer's punctuation policy for Chinese. Installed library
    # files are not changed; this applies only to this report-building process.
    chinese_closing = "，；：？！）》】”’"
    textsplit.ALL_CANNOT_START += chinese_closing
    paragraph_layout.ALL_CANNOT_START += chinese_closing
    pdfmetrics.registerFont(TTFont("BodyCN", str(font_dir / "simsun.ttc"),
                                 subfontIndex=0))
    pdfmetrics.registerFont(TTFont("HeadCN", str(font_dir / "simhei.ttf")))
    latin_candidates = [
        font_dir / "arial.ttf",
        Path("C:/Users/xuanm/.cache/codex-runtimes/codex-primary-runtime/"
             "dependencies/native/poppler/Library/share/fonts/DejaVuSans.ttf"),
    ]
    latin = next((p for p in latin_candidates if p.is_file()), None)
    if latin is None:
        raise FileNotFoundError("Provide arial.ttf in --font-dir for symbols.")
    pdfmetrics.registerFont(TTFont("Symbols", str(latin)))
    pdfmetrics.registerFontFamily("BodyCN", normal="BodyCN", bold="HeadCN",
                                 italic="BodyCN", boldItalic="HeadCN")


def rich(text, reference=False):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    for symbol in "ħπσΓωΔφψε²³±×→":
        text = text.replace(symbol, f'<font name="Symbols">{symbol}</font>')
    if reference:
        text = re.sub(
            r"(10\.\d{4,9}/[A-Za-z0-9./()-]+)",
            lambda m: (
                '<a color="#17657B" href="https://doi.org/'
                + m[1].rstrip(".") + '">' + m[1].rstrip(".") + "</a>"
                + ("." if m[1].endswith(".") else "")
            ),
            text,
        )
    return text


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.heading_index = 0

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in (
                "chapter", "cover_title"):
            self.heading_index += 1
            name = f"section-{self.heading_index}"
            self.canv.bookmarkPage(name)
            self.canv.addOutlineEntry(flowable.getPlainText(), name, 0, False)


def footer(canvas, doc):
    width, height = A4
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(.45)
        canvas.line(doc.leftMargin, height - 15 * mm,
                    width - doc.rightMargin, height - 15 * mm)
        canvas.setFont("HeadCN", 8.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, height - 12.2 * mm,
                          "自旋波传播研究整理报告")
    canvas.setFillColor(MUTED)
    canvas.setFont("BodyCN", 9)
    canvas.drawCentredString(width / 2, 12 * mm, str(doc.page))
    canvas.restoreState()


def styles():
    common = dict(fontName="BodyCN", textColor=INK, wordWrap="CJK",
                  allowWidows=0, allowOrphans=0)
    return {
        "body": ParagraphStyle(
            "body", fontSize=11.2, leading=18.4, firstLineIndent=22.4,
            spaceAfter=9, alignment=TA_LEFT, **common),
        "chapter": ParagraphStyle(
            "chapter", fontName="HeadCN", fontSize=19, leading=27,
            textColor=INK, wordWrap="CJK", spaceAfter=16, keepWithNext=True),
        "section": ParagraphStyle(
            "section", fontName="HeadCN", fontSize=13, leading=20,
            textColor=INK, wordWrap="CJK", spaceBefore=7, spaceAfter=9,
            keepWithNext=True),
        "cover_title": ParagraphStyle(
            "cover_title", fontName="HeadCN", fontSize=27, leading=38,
            textColor=INK, spaceBefore=15, spaceAfter=12, wordWrap="CJK"),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="HeadCN", fontSize=14, leading=23,
            textColor=MUTED, spaceAfter=10, wordWrap="CJK"),
        "date": ParagraphStyle(
            "date", fontSize=10.2, leading=16, textColor=MUTED,
            fontName="BodyCN", spaceAfter=23),
        "caption": ParagraphStyle(
            "caption", fontName="BodyCN", fontSize=9.4, leading=14.2,
            textColor=MUTED, wordWrap="CJK", spaceAfter=12),
        "cell": ParagraphStyle(
            "cell", fontSize=10.1, leading=15.5, **common),
        "cell_head": ParagraphStyle(
            "cell_head", fontName="HeadCN", fontSize=10.1, leading=15.5,
            textColor=INK, wordWrap="CJK"),
        "reference": ParagraphStyle(
            "reference", fontSize=9.4, leading=13.8, firstLineIndent=0,
            spaceAfter=10, **common),
    }


def table_from(lines, width, sty):
    parsed = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    parsed = [r for r in parsed if not all(re.fullmatch(r"[-: ]+", c) for c in r)]
    count = len(parsed[0])
    if count == 2:
        widths = [width * .32, width * .68]
    else:
        widths = [width * .5] + [width * .5 / (count - 1)] * (count - 1)
    rows = [
        [Paragraph(rich(c), sty["cell_head"] if i == 0 else sty["cell"])
         for c in row]
        for i, row in enumerate(parsed)
    ]
    table = Table(rows, colWidths=widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("LINEABOVE", (0, 0), (-1, 0), .6, RULE),
        ("LINEBELOW", (0, 0), (-1, -1), .35, RULE),
    ]))
    return [table, Spacer(1, 11)]


def build(output):
    sty = styles()
    doc = ReportDoc(
        str(output), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=22 * mm, bottomMargin=19 * mm,
        title="自旋波传播研究整理报告",
        author="", subject="模型、模拟、文献与四个后续方向的整理",
        pageCompression=1,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=footer))
    chunks = (HERE / "report.md").read_text(encoding="utf-8").split("<!-- page -->")
    story = []
    for page_index, chunk in enumerate(chunks):
        if page_index:
            story.append(PageBreak())
        lines = chunk.strip().splitlines()
        i = 0
        paragraph_number = 0
        references = chunk.lstrip().startswith("# 参考文献")
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith("# "):
                key = "cover_title" if page_index == 0 else "chapter"
                story.append(Paragraph(rich(line[2:]), sty[key]))
                i += 1
                continue
            if line.startswith("## "):
                story.append(Paragraph(rich(line[3:]), sty["section"]))
                i += 1
                continue
            if line.startswith("|"):
                block = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    block.append(lines[i].strip())
                    i += 1
                story.extend(table_from(block, doc.width, sty))
                continue
            match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", line)
            if match:
                caption, name = match.groups()
                path = HERE / name
                with PILImage.open(path) as im:
                    width, height = im.size
                scale = min(doc.width / width, 82 * mm / height)
                figure = Image(str(path), width=width * scale, height=height * scale)
                figure.hAlign = "CENTER"
                story.append(KeepTogether([
                    Spacer(1, 4), figure, Spacer(1, 6),
                    Paragraph(rich(caption), sty["caption"]),
                ]))
                i += 1
                continue
            text = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(
                    ("#", "|", "![")):
                text.append(lines[i].strip())
                i += 1
            paragraph_number += 1
            key = "reference" if references else "body"
            if page_index == 0 and paragraph_number <= 2:
                key = "subtitle" if paragraph_number == 1 else "date"
            story.append(Paragraph(rich(" ".join(text), reference=references), sty[key]))
    doc.build(story)
    (HERE / "build-info.json").write_text(json.dumps({
        "source": "report.md", "output": str(output.name),
        "planned_sections": len(chunks), "engine": "ReportLab",
        "fonts": ["simsun.ttc", "simhei.ttf", "arial.ttf"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    parser.add_argument("--output", type=Path,
                        default=PACKAGE / "自旋波研究整理报告.pdf")
    args = parser.parse_args()
    register_fonts(args.font_dir)
    build(args.output)
