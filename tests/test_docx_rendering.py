"""DOCX visual-rendering layer tests.

The renderer needs LibreOffice, which may be absent on CI. Detection and the
graceful fallback are always tested; the real conversion runs only when
LibreOffice is installed.
"""

import pytest

pytest.importorskip("docx")

from docx import Document  # noqa: E402

from pdfqc.rendering import docx_to_pdf_bytes, find_soffice  # noqa: E402


def _docx_bytes(paragraphs):
    import io

    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_convert_returns_none_without_soffice():
    # Explicit bogus path -> subprocess fails -> graceful None (fallback path).
    assert docx_to_pdf_bytes(b"not a real docx", soffice="/no/such/soffice") is None


def test_find_soffice_returns_str_or_none():
    result = find_soffice()
    assert result is None or isinstance(result, str)


@pytest.mark.skipif(find_soffice() is None, reason="LibreOffice not installed")
def test_real_conversion_produces_pdf():
    pdf = docx_to_pdf_bytes(_docx_bytes(["Hello page one."]))
    assert pdf is not None and pdf[:5] == b"%PDF-"
