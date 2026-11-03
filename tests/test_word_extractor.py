"""DOCX extraction + DOCX/PDF comparison tests.

Fixtures are generated on the fly with python-docx so no binary sample files
need to be committed.
"""

import pytest

pytest.importorskip("docx")

from docx import Document  # noqa: E402

from pdfqc.comparators import ComparisonEngine  # noqa: E402
from pdfqc.extractors import WordExtractor, detect_type, get_extractor  # noqa: E402
from pdfqc.models import (  # noqa: E402
    DiffType,
    ExtractionMethod,
    ExtractionResult,
    PageContent,
)


def _make_docx(path, paragraphs, table=None, page_break_before=None):
    doc = Document()
    for i, text in enumerate(paragraphs):
        p = doc.add_paragraph(text)
        if page_break_before is not None and i == page_break_before:
            p.paragraph_format.page_break_before = True
    if table:
        t = doc.add_table(rows=len(table), cols=len(table[0]))
        for r, row in enumerate(table):
            for c, val in enumerate(row):
                t.cell(r, c).text = val
    doc.save(str(path))
    return str(path)


def test_detect_type():
    assert detect_type("a.docx") == "docx"
    assert detect_type("A.DOCX") == "docx"
    assert detect_type("a.pdf") == "pdf"


def test_get_extractor_docx_returns_word_extractor():
    assert isinstance(get_extractor("docx"), WordExtractor)


def test_docx_text_extraction(tmp_path):
    path = _make_docx(tmp_path / "d.docx", ["Hello world.", "Second line."])
    res = WordExtractor().extract(path)
    assert isinstance(res, ExtractionResult)
    assert res.pages[0].method == ExtractionMethod.DOCX
    assert "Hello world." in res.pages[0].text
    assert "Second line." in res.pages[0].text


def test_docx_table_extraction(tmp_path):
    path = _make_docx(tmp_path / "t.docx", ["Intro."],
                      table=[["A", "1"], ["B", "2"]])
    res = WordExtractor().extract(path)
    assert res.pages[0].tables == [[["A", "1"], ["B", "2"]]]
    # Table text also present in the page text stream (mirrors PDF behaviour).
    assert "A 1" in res.pages[0].text


def test_docx_page_break_splits_pages(tmp_path):
    path = _make_docx(tmp_path / "p.docx", ["Page one.", "Page two."],
                      page_break_before=1)
    res = WordExtractor().extract(path)
    assert res.page_count == 2
    assert "Page one." in res.pages[0].text
    assert "Page two." in res.pages[1].text


def test_docx_manual_page_breaks_all_pages(tmp_path):
    doc = Document()
    doc.add_paragraph("AAA")
    doc.add_page_break()
    doc.add_paragraph("BBB")
    doc.add_page_break()
    doc.add_paragraph("CCC")
    doc.save(str(tmp_path / "m.docx"))
    res = WordExtractor().extract(str(tmp_path / "m.docx"))
    assert [p.text for p in res.pages] == ["AAA", "BBB", "CCC"]


def test_docx_section_breaks_all_pages(tmp_path):
    """Regression: next-page section breaks must produce all pages, not one."""
    from docx.enum.section import WD_SECTION

    doc = Document()
    doc.add_paragraph("AAA")
    doc.add_section(WD_SECTION.NEW_PAGE)
    doc.add_paragraph("BBB")
    doc.add_section(WD_SECTION.NEW_PAGE)
    doc.add_paragraph("CCC")
    doc.save(str(tmp_path / "s.docx"))
    res = WordExtractor().extract(str(tmp_path / "s.docx"))
    assert res.page_count == 3
    assert [p.text for p in res.pages] == ["AAA", "BBB", "CCC"]


def test_docx_vs_docx_comparison(tmp_path):
    a = _make_docx(tmp_path / "a.docx", ["Total is 100 dollars.", "Keep this line."])
    b = _make_docx(tmp_path / "b.docx", ["Total is 250 dollars.", "Keep this line."])
    m = WordExtractor().extract(a)
    p = WordExtractor().extract(b)
    diffs = ComparisonEngine().compare(m, p)
    assert DiffType.CHANGED_VALUE in [d.diff_type for d in diffs]


def test_docx_vs_pdf_comparison_is_type_agnostic(tmp_path):
    """DOCX on one side, a PDF-style ExtractionResult on the other."""
    path = _make_docx(tmp_path / "m.docx", ["Growth of 10% expected.", "Shared text."])
    markup = WordExtractor().extract(path)
    proxy = ExtractionResult(
        "proxy.pdf",
        pages=[PageContent(1, "Growth of 25% expected.\nShared text.",
                           ExtractionMethod.TEXT)],
    )
    diffs = ComparisonEngine().compare(markup, proxy)
    assert DiffType.CHANGED_PERCENT in [d.diff_type for d in diffs]


def test_docx_table_participates_in_comparison(tmp_path):
    a = _make_docx(tmp_path / "ta.docx", ["Head."], table=[["X", "1"]])
    b = _make_docx(tmp_path / "tb.docx", ["Head."], table=[["X", "9"]])
    diffs = ComparisonEngine().compare(
        WordExtractor().extract(a), WordExtractor().extract(b)
    )
    table_diffs = [d for d in diffs if d.diff_type == DiffType.TABLE]
    assert any(d.expected == "1" and d.actual == "9" for d in table_diffs)
