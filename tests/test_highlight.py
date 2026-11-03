"""Character-level highlight detection (issue #1)."""

from pdfqc.highlight import canon, changed_tokens, diffkey, locate


def test_diffkey_preserves_punctuation_and_case():
    assert diffkey("approved.") != diffkey("approved")
    assert diffkey("Important!") != diffkey("Important.")
    assert diffkey("The") != diffkey("the")


def test_diffkey_unifies_only_unicode_variants():
    assert diffkey("“Hi”") == diffkey('"Hi"')     # smart vs straight quotes
    assert diffkey("co–op") == diffkey("co-op")         # en-dash vs hyphen


def test_missing_period_is_a_changed_token():
    assert changed_tokens("The product is approved.",
                          "The product is approved", "markup") == {"approved."}


def test_punctuation_swap_detected():
    assert changed_tokens("Important!", "Important.", "markup") == {"Important!"}
    assert changed_tokens("a: b", "a; b", "markup") == {"a:"}


def test_single_char_difference_detected():
    assert changed_tokens("colour", "color", "markup") == {"colour"}


def test_identical_text_has_no_changed_tokens():
    assert changed_tokens("same text here", "same text here", "markup") == set()


def test_locate_highlights_only_changed_word_and_respects_suppression():
    page = ["The", "product", "is", "approved."]
    changed = {"approved."}
    other = {"The", "product", "is", "approved"}  # other doc lacks the period
    idx = locate(page, "The product is approved.", changed, other)
    assert idx == [3]  # only the word carrying the extra period


def test_locate_suppresses_token_present_verbatim_in_other_doc():
    # mis-alignment noise: token identical in both -> not highlighted
    page = ["average", "annual", "return"]
    assert locate(page, "average annual return", {"average"},
                  {"average", "annual", "return"}) == []


def test_identical_numbers_not_changed():
    assert changed_tokens("Total 12.50", "Total 12.50", "markup") == set()


def test_changed_number_detected():
    assert changed_tokens("Total 12.50", "Total 12.55", "markup") == {"12.50"}


def test_canon_still_strips_punctuation():
    assert canon("Approved.") == "approved"
