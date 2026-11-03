from pdfqc.normalizers.normalizer import normalize_text, to_segments


def test_collapses_whitespace_and_newlines():
    assert normalize_text("a   b\n\n c") == "a b\nc"


def test_normalizes_smart_quotes_and_dashes():
    assert normalize_text("“Hi” – it’s") == '"Hi" - it\'s'


def test_rejoins_hyphenated_line_wrap():
    assert normalize_text("compar-\nison") == "comparison"


def test_sentence_segments_ignore_line_wrapping():
    text = "The quick brown\nfox. Jumps over."
    assert to_segments(text) == ["The quick brown fox.", "Jumps over."]


def test_line_segments_keep_lines():
    assert to_segments("one\ntwo", mode="line") == ["one", "two"]


def test_empty_text_returns_empty_segments():
    assert to_segments("   ") == []
