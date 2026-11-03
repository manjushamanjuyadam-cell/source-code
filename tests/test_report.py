from pdfqc.models import (
    Difference,
    DiffType,
    ExtractionMethod,
    ExtractionResult,
    PageContent,
)
from pdfqc.reports import ReportGenerator, build_report


def _doc(path):
    return ExtractionResult(path, pages=[PageContent(1, "x", ExtractionMethod.TEXT)])


def test_report_counts_by_type():
    diffs = [
        Difference(DiffType.MISSING, "a", "", "Page 1"),
        Difference(DiffType.CHANGED_VALUE, "1", "2", "Page 1"),
    ]
    report = build_report(_doc("m.pdf"), _doc("p.pdf"), diffs)
    assert report.total == 2
    assert report.count(DiffType.MISSING) == 1
    assert report.pages_compared == 1


def test_generate_contains_summary_and_details():
    diffs = [Difference(DiffType.MISSING, "lost line", "", "Page 1")]
    report = build_report(_doc("m.pdf"), _doc("p.pdf"), diffs)
    text = ReportGenerator().generate(report)
    assert "PDF QC Comparison Report" in text
    assert "Missing content" in text
    assert "lost line" in text


def test_generate_handles_no_differences():
    report = build_report(_doc("m.pdf"), _doc("p.pdf"), [])
    text = ReportGenerator().generate(report)
    assert "No differences found" in text


def test_save_writes_file(tmp_path):
    report = build_report(_doc("m.pdf"), _doc("p.pdf"), [])
    out = tmp_path / "report.md"
    ReportGenerator().save(report, str(out))
    assert out.read_text(encoding="utf-8").startswith("# PDF QC Comparison Report")
