"""Extractor tests.

Real PDF/OCR extraction needs the pdfplumber, Pillow and Tesseract runtime,
so the routing logic is tested with lightweight fakes instead. The hybrid
decision (digital text vs OCR) is the interesting behaviour to lock down.
"""

import sys
import types

import pytest

from pdfqc.config import Config
from pdfqc.models import ExtractionMethod


class _FakeImage:
    def __init__(self, original="IMG"):
        self.original = original


class _FakePage:
    def __init__(self, text, image_text="OCR-TEXT"):
        self._text = text
        self._image_text = image_text

    def extract_text(self):
        return self._text

    def extract_tables(self):
        return []

    def to_image(self, resolution=300):
        return _FakeImage(self._image_text)


class _FakePDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _install_fake_pdfplumber(monkeypatch, pages):
    module = types.ModuleType("pdfplumber")
    module.open = lambda path: _FakePDF(pages)
    monkeypatch.setitem(sys.modules, "pdfplumber", module)


@pytest.fixture(autouse=True)
def _patch_ocr(monkeypatch):
    # Avoid needing the real Tesseract binary.
    monkeypatch.setattr(
        "pdfqc.extractors.hybrid_extractor.image_to_text",
        lambda image, config: image if isinstance(image, str) else "OCR",
    )


def test_hybrid_uses_text_when_digital_present(monkeypatch):
    from pdfqc.extractors import HybridExtractor

    _install_fake_pdfplumber(monkeypatch, [_FakePage("This page has real text.")])
    result = HybridExtractor(Config()).extract("doc.pdf")
    assert result.pages[0].method == ExtractionMethod.TEXT
    assert "real text" in result.pages[0].text


def test_hybrid_falls_back_to_ocr_when_no_text(monkeypatch):
    from pdfqc.extractors import HybridExtractor

    _install_fake_pdfplumber(monkeypatch, [_FakePage("", image_text="SCANNED")])
    result = HybridExtractor(Config()).extract("doc.pdf")
    assert result.pages[0].method == ExtractionMethod.OCR
    assert result.pages[0].text == "SCANNED"


def test_text_extractor_reads_pages(monkeypatch):
    from pdfqc.extractors import TextExtractor

    _install_fake_pdfplumber(
        monkeypatch, [_FakePage("Page A"), _FakePage("Page B")]
    )
    result = TextExtractor().extract("doc.pdf")
    assert result.page_count == 2
    assert result.pages[1].text == "Page B"
