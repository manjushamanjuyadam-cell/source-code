"""Proxy spell-check tests. Priority: LOW false positives."""

import pytest

pytest.importorskip("spellchecker")
pytest.importorskip("docx")

import os  # noqa: E402

from docx import Document  # noqa: E402

from pdfqc.extractors import TextExtractor, WordExtractor  # noqa: E402
from pdfqc.spellcheck import ProxySpellChecker, load_custom_terms  # noqa: E402

CUSTOM = load_custom_terms()


def _flagged(text):
    return {i.word: i.suggestion for i in ProxySpellChecker(CUSTOM).check_page(text, 1)}


def test_correct_text_has_no_issues():
    assert _flagged("the fund will send you a form for the calendar year") == {}


def test_obvious_misspelling_flagged():
    assert "distribtion" in _flagged("the distribtion amount was paid")


def test_company_name_not_flagged():
    assert _flagged("Eaton Vance Broadridge") == {}


def test_financial_terms_not_flagged():
    assert _flagged("cumulative annualized reinvested distribution shareholder") == {}


def test_acronyms_not_flagged():
    assert _flagged("NYSE ETV NAV DIV IRA") == {}


def test_numbers_currency_date_percent_not_flagged():
    assert _flagged("100 $0.0949 01/31/2024 8.49% 2,500") == {}


def test_hyphenated_terms_not_flagged():
    assert _flagged("Tax-Managed Buy-Write year-to-date short-term") == {}


def test_url_and_email_not_flagged():
    assert _flagged("visit https://example.com or email john@example.com") == {}


def test_ocr_garbage_not_flagged():
    # No plausible single-edit correction -> stay silent.
    assert _flagged("Tud-ZTZ00N A82BL2 mG rn cl") == {}


def test_custom_dictionary_suppresses_terms():
    text = "wibblex Eaton"
    assert not ProxySpellChecker({"wibblex"}).check_page(text, 1)


def test_digital_pdf_proxy(tmp_path):
    # Use extracted text path (extractor tested elsewhere); here feed text.
    checker = ProxySpellChecker(CUSTOM)
    issues = checker.check_pages(["clean digital text here", "a recieved typo"])
    assert any(i.word == "recieved" and i.page == 2 for i in issues)


def test_docx_proxy(tmp_path):
    doc = Document()
    doc.add_paragraph("The payment was recieved on time.")
    path = str(tmp_path / "p.docx")
    doc.save(path)
    res = WordExtractor().extract(path)
    issues = ProxySpellChecker(CUSTOM).check_pages([p.text for p in res.pages])
    assert any(i.word == "recieved" for i in issues)


@pytest.mark.skipif(
    not os.path.exists("samples/_proxy_ocr.txt"),
    reason="real OCR proxy sample not present",
)
def test_real_ocr_proxy_low_false_positives():
    text = open("samples/_proxy_ocr.txt", encoding="utf-8").read()
    issues = ProxySpellChecker(CUSTOM).check_page(text, 1)
    # Conservative: the real scanned proxy must not produce a wall of issues.
    assert len(issues) <= 3, [i.word for i in issues]
