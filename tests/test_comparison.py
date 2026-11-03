from pdfqc.comparators import ComparisonEngine
from pdfqc.models import (
    DiffType,
    ExtractionMethod,
    ExtractionResult,
    PageContent,
)


def _doc(text="", tables=None):
    return ExtractionResult(
        source_path="x",
        pages=[PageContent(1, text, ExtractionMethod.TEXT, tables or [])],
    )


def _types(diffs):
    return [d.diff_type for d in diffs]


def test_identical_documents_have_no_differences():
    doc = _doc("Hello world. All good.")
    assert ComparisonEngine().compare(doc, doc) == []


def test_missing_period_detected():
    m = _doc("The product is approved.")
    p = _doc("The product is approved")
    assert ComparisonEngine().compare(m, p)  # a difference is reported


def test_punctuation_swap_detected():
    m = _doc("Important!")
    p = _doc("Important.")
    assert ComparisonEngine().compare(m, p)


def test_identical_table_numbers_not_flagged():
    m = _doc(tables=[[["Amount", "12.50"], ["Count", "100"]]])
    p = _doc(tables=[[["Amount", "12.50"], ["Count", "100"]]])
    assert [d for d in ComparisonEngine().compare(m, p)
            if d.diff_type == DiffType.TABLE] == []


def test_changed_table_number_flagged():
    m = _doc(tables=[[["Amount", "12.50"]]])
    p = _doc(tables=[[["Amount", "12.55"]]])
    tdiffs = [d for d in ComparisonEngine().compare(m, p)
              if d.diff_type == DiffType.TABLE]
    assert any(d.expected == "12.50" and d.actual == "12.55" for d in tdiffs)


def test_structural_table_noise_does_not_flag_identical_values():
    # Same visible values, but extraction split one table with an extra blank
    # cell/row. Strict positional compare would flag identical numbers; the
    # difflib alignment must not.
    m = _doc(tables=[[["A", "100"], ["B", "200"]]])
    p = _doc(tables=[[[""], ["A", "100"], ["B", "200"]]])
    tdiffs = [d for d in ComparisonEngine().compare(m, p)
              if d.diff_type == DiffType.TABLE
              and d.expected.strip() and d.actual.strip()]
    assert tdiffs == []  # no identical value falsely reported as changed


def test_missing_sentence_detected():
    m = _doc("Keep this. Remove this.")
    p = _doc("Keep this.")
    diffs = ComparisonEngine().compare(m, p)
    assert DiffType.MISSING in _types(diffs)


def test_additional_sentence_detected():
    m = _doc("Keep this.")
    p = _doc("Keep this. Extra one.")
    diffs = ComparisonEngine().compare(m, p)
    assert DiffType.ADDITIONAL in _types(diffs)


def test_changed_value_detected():
    m = _doc("Total is 100 dollars.")
    p = _doc("Total is 250 dollars.")
    diffs = ComparisonEngine().compare(m, p)
    assert DiffType.CHANGED_VALUE in _types(diffs)


def test_changed_percent_detected():
    m = _doc("Growth of 10% expected.")
    p = _doc("Growth of 25% expected.")
    diffs = ComparisonEngine().compare(m, p)
    assert DiffType.CHANGED_PERCENT in _types(diffs)


def test_changed_date_detected():
    m = _doc("Due on 01/02/2024 sharp.")
    p = _doc("Due on 03/04/2025 sharp.")
    diffs = ComparisonEngine().compare(m, p)
    assert DiffType.CHANGED_DATE in _types(diffs)


def test_generic_text_change_detected():
    m = _doc("The colour is red.")
    p = _doc("The colour is blue.")
    diffs = ComparisonEngine().compare(m, p)
    assert DiffType.CHANGED in _types(diffs)


def test_table_cell_change_detected():
    m = _doc(tables=[[["A", "1"], ["B", "2"]]])
    p = _doc(tables=[[["A", "1"], ["B", "9"]]])
    diffs = ComparisonEngine().compare(m, p)
    table_diffs = [d for d in diffs if d.diff_type == DiffType.TABLE]
    assert len(table_diffs) == 1
    assert table_diffs[0].expected == "2"
    assert table_diffs[0].actual == "9"


def test_page_count_mismatch_reports_missing_page_content():
    m = ExtractionResult(
        "x",
        pages=[
            PageContent(1, "Page one text here.", ExtractionMethod.TEXT),
            PageContent(2, "Page two only in markup.", ExtractionMethod.TEXT),
        ],
    )
    p = _doc("Page one text here.")
    diffs = ComparisonEngine().compare(m, p)
    assert any(d.location == "Page 2" for d in diffs)
