"""Reviewer-focused PDF comparison UI.

The PDF pages are the primary interface: both documents are rendered and the
differences reported by the comparison engine are highlighted directly on the
pages. UI only — extraction, OCR, normalization and comparison logic are reused
unchanged from `pdfqc`. Word locations for highlighting are resolved in this UI
layer (pdfplumber words for digital pages, Tesseract word boxes for OCR pages).

Run:  python -m streamlit run app.py
"""

from __future__ import annotations

import html
import io
import os
import re
import tempfile

import streamlit as st
from PIL import Image, ImageDraw

from pdfqc.comparators import ComparisonEngine
from pdfqc.config import Config
from pdfqc.dependencies import find_tesseract
from pdfqc.extractors import detect_type, get_extractor
from pdfqc.highlight import canon as _canon
from pdfqc.highlight import changed_tokens, locate, token_keys
from pdfqc.models import DiffType, ExtractionResult

VIEW_DPI = 150  # rendering + OCR-box resolution for the viewers (display only)

# Highlight colors (RGB). Yellow = modified, Red = missing, Blue = additional.
# Purple is a DEDICATED spell-check color, separate from comparison colors.
RGB = {
    "modified": (240, 200, 0),
    "missing": (210, 45, 45),
    "additional": (30, 105, 210),
}
SPELL_RGB = (150, 60, 200)  # purple = potential spelling issue
RGB["spell"] = SPELL_RGB
HEX = {k: "#%02x%02x%02x" % v for k, v in RGB.items()}
TYPE_KIND = {
    DiffType.MISSING: "missing",
    DiffType.ADDITIONAL: "additional",
    DiffType.CHANGED: "modified",
    DiffType.CHANGED_VALUE: "modified",
    DiffType.CHANGED_DATE: "modified",
    DiffType.CHANGED_PERCENT: "modified",
    DiffType.TABLE: "modified",
}


# --- pipeline (reused, cached) ----------------------------------------------
@st.cache_data(show_spinner=False)
def _extract(data: bytes, name: str, doc_type: str, mode: str,
             cfg_kwargs: dict) -> ExtractionResult:
    config = Config(**cfg_kwargs)
    extractor = get_extractor(doc_type, mode, config)
    suffix = ".docx" if doc_type == "docx" else ".pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(data)
        tmp.close()
        result = extractor.extract(tmp.name)
    finally:
        os.unlink(tmp.name)
    result.source_path = name
    return result


# --- proxy spell check (optional, separate from comparison) ------------------
@st.cache_data(show_spinner=False)
def _spell_check(page_texts: list[str]) -> list[dict]:
    """Run the conservative proxy spell checker. Cached so Streamlit reruns do
    not recompute; a fresh click with new input recomputes automatically."""
    from pdfqc.spellcheck import ProxySpellChecker, load_custom_terms

    checker = ProxySpellChecker(load_custom_terms())
    return [
        {"word": i.word, "suggestion": i.suggestion, "page": i.page}
        for i in checker.check_pages(page_texts)
    ]


# --- DOCX visual rendering layer (display only) -----------------------------
@st.cache_data(show_spinner=False)
def _docx_pdf(data: bytes) -> bytes | None:
    """Render DOCX bytes to a laid-out PDF via LibreOffice (None if absent)."""
    from pdfqc.rendering import docx_to_pdf_bytes

    return docx_to_pdf_bytes(data)


@st.cache_data(show_spinner=False)
def _pdf_page_count(data: bytes) -> int:
    import pdfplumber

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        tmp.write(data)
        tmp.close()
        with pdfplumber.open(tmp.name) as pdf:
            return len(pdf.pages)
    finally:
        os.unlink(tmp.name)


# --- page rendering + word locations (UI layer) -----------------------------
@st.cache_data(show_spinner=False)
def _render(data: bytes, page: int, dpi: int) -> bytes:
    import pdfplumber

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        tmp.write(data)
        tmp.close()
        with pdfplumber.open(tmp.name) as pdf:
            image = pdf.pages[page].to_image(resolution=dpi).original
    finally:
        os.unlink(tmp.name)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


@st.cache_data(show_spinner=False)
def _word_boxes(data: bytes, page: int, method: str, dpi: int,
                tess: str, lang: str) -> list[dict]:
    """Return [{text, box=(x0,y0,x1,y1)}] in image pixels at ``dpi``."""
    import pdfplumber

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    words: list[dict] = []
    try:
        tmp.write(data)
        tmp.close()
        with pdfplumber.open(tmp.name) as pdf:
            pg = pdf.pages[page]
            if method == "ocr":
                import pytesseract
                from pytesseract import Output

                if tess:
                    pytesseract.pytesseract.tesseract_cmd = tess
                image = pg.to_image(resolution=dpi).original
                data_d = pytesseract.image_to_data(
                    image, lang=lang, output_type=Output.DICT
                )
                for i, txt in enumerate(data_d["text"]):
                    if txt.strip():
                        x, y = data_d["left"][i], data_d["top"][i]
                        w, h = data_d["width"][i], data_d["height"][i]
                        words.append({"text": txt, "box": (x, y, x + w, y + h)})
            else:
                s = dpi / 72.0
                for w in pg.extract_words():
                    words.append({
                        "text": w["text"],
                        "box": (w["x0"] * s, w["top"] * s, w["x1"] * s, w["bottom"] * s),
                    })
    finally:
        os.unlink(tmp.name)
    return words


def _highlighted(img_bytes: bytes, highlights: list[tuple]) -> bytes:
    base = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for box, rgb, current in highlights:
        pad = (box[0] - 2, box[1] - 2, box[2] + 2, box[3] + 2)
        draw.rectangle(pad, fill=(*rgb, 90))
        if current:
            draw.rectangle(pad, outline=(*rgb, 255), width=3)
    out = Image.alpha_composite(base, overlay).convert("RGB")
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()


def _page_of(location: str) -> int:
    m = re.search(r"Page\s+(\d+)", location)
    return int(m.group(1)) - 1 if m else 0


def _diffs_for(res: dict, page: int, agnostic: bool) -> list:
    """Diffs to consider for a page. Native PDF/text pages align with the diff
    'Page N' numbering (agnostic=False). A rendered DOCX has its own layout
    pagination that need not match, so it considers ALL diffs and locates them
    by text on each page (agnostic=True)."""
    if agnostic:
        return res["diffs"]
    return [d for d in res["diffs"] if _page_of(d.location) == page]


def _other_tok(res: dict, side: str, page: int, agnostic: bool) -> set[str]:
    other = res["proxy"] if side == "markup" else res["markup"]
    if agnostic:
        txt = " ".join(p.text for p in other.pages)
    else:
        txt = other.pages[page].text if page < other.page_count else ""
    return token_keys(txt)


def _highlight_map(word_texts: list[str], diffs: list, side: str,
                   other_tokens: set[str], current) -> dict:
    """Per-word highlight plan for a page: {word_index: (kind, is_cur)}.

    Pure: caller supplies the page's word texts (from PDF word boxes or DOCX
    page text), the diffs to consider and the suppression token set. Changed
    tokens are detected punctuation/case-sensitively (via the highlight module)
    so small character differences are highlighted precisely."""
    out: dict = {}
    for d in diffs:
        if d.diff_type == DiffType.TABLE and not (d.expected.strip() and d.actual.strip()):
            continue
        kind = TYPE_KIND.get(d.diff_type, "modified")
        target = d.expected if side == "markup" else d.actual
        if not target.strip():
            continue
        changed = changed_tokens(d.expected, d.actual, side)
        if not changed:
            continue
        is_cur = d is current
        for idx in locate(word_texts, target, changed, other_tokens):
            prev = out.get(idx)
            out[idx] = (kind, is_cur or (prev[1] if prev else False))
    return out


def _docx_html(text: str, hmap: dict) -> str:
    """Render DOCX page text with changed tokens wrapped in colored spans.
    Word indices match ``text.split()`` order used to build ``hmap``."""
    lines, i = [], 0
    for line in text.split("\n"):
        parts = []
        for w in line.split():
            cell = html.escape(w)
            if i in hmap:
                kind = hmap[i][0]
                parts.append(
                    f"<span style='background:{HEX[kind]};color:#000;"
                    f"border-radius:3px;padding:0 2px'>{cell}</span>"
                )
            else:
                parts.append(cell)
            i += 1
        lines.append(" ".join(parts))
    body = "<br>".join(lines)
    return (
        "<div style='white-space:normal;line-height:1.6;font-family:Georgia,serif;"
        "border:1px solid #ccc;border-radius:6px;padding:12px;max-height:75vh;"
        f"overflow:auto'>{body}</div>"
    )


def _docx_tables_html(tables: list) -> str:
    """Render extracted DOCX tables as real bordered HTML tables so the grid /
    cell structure is preserved in the text-view fallback (used when LibreOffice
    is not available). Reconstructs the actual extracted cells — it does not draw
    artificial borders over arbitrary text."""
    if not tables:
        return ""
    out = ["<div style='margin-top:10px'>"]
    for t in tables:
        out.append(
            "<table style='border-collapse:collapse;margin:8px 0;"
            "font-family:Georgia,serif;font-size:0.9rem'>"
        )
        for row in t:
            out.append("<tr>")
            for cell in row:
                out.append(
                    "<td style='border:1px solid #555;padding:3px 8px;"
                    f"vertical-align:top'>{html.escape(cell)}</td>"
                )
            out.append("</tr>")
        out.append("</table>")
    out.append("</div>")
    return "".join(out)


# --- page -------------------------------------------------------------------
APP_NAME = "PDF QC Comparison Tool"
APP_TAGLINE = "Local Enterprise Document QC Application"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            f"### {APP_NAME}\n{APP_TAGLINE}\n\n"
            "Compares a Markup document against a Proxy document (PDF or DOCX) "
            "and reports missing, additional and changed content. Runs fully "
            "locally — no cloud, no AI services.\n\n"
            "Built with open-source components; see THIRD_PARTY_NOTICES.txt."
        ),
        "Get Help": None,
        "Report a bug": None,
    },
)

# Hide default Streamlit chrome (menu / deploy / status / footer) SURGICALLY.
# We must NOT hide the whole toolbar: in Streamlit 1.63 the sidebar "expand"
# button (stExpandSidebarButton) lives in that region, and hiding the toolbar
# hid it, leaving no way to reopen the sidebar once collapsed.
st.markdown(
    """
    <style>
      #MainMenu, [data-testid="stMainMenu"] {visibility: hidden;}
      footer {visibility: hidden;}
      [data-testid="stToolbarActions"] {visibility: hidden;}
      [data-testid="stStatusWidget"] {visibility: hidden;}
      [data-testid="stAppDeployButton"] {display: none !important;}

      /* Always keep the sidebar open/close controls visible and clickable so
         the navigation panel can be reopened after it is collapsed. Both the
         1.63 test-ids and older ones are targeted for safety. */
      [data-testid="stExpandSidebarButton"],
      [data-testid="stSidebarCollapseButton"],
      [data-testid="stSidebarCollapsedControl"],
      [data-testid="collapsedControl"] {
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 1000 !important;
      }
      [data-testid="stExpandSidebarButton"] button {
        background: #963cc8 !important;
        color: #fff !important;
        border-radius: 6px !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(f"## {APP_NAME}")
st.markdown(
    "**Legend:** "
    "<span style='background:#f0c800;color:#000;padding:1px 8px;border-radius:8px'>Yellow = Modified</span> "
    "<span style='background:#d22d2d;color:#fff;padding:1px 8px;border-radius:8px'>Red = Missing</span> "
    "<span style='background:#1e69d2;color:#fff;padding:1px 8px;border-radius:8px'>Blue = Additional</span> "
    "<span style='background:#963cc8;color:#fff;padding:1px 8px;border-radius:8px'>Purple = Potential spelling issue (Proxy)</span>",
    unsafe_allow_html=True,
)

# Early, non-blocking notice if the OCR engine is missing. Uses the existing
# resolver (no second detection mechanism). Only informs the user; OCR is needed
# only for scanned PDFs, so the app stays fully usable. The Compare-time friendly
# error for scanned PDFs is unchanged and still protects that case.
if not find_tesseract():
    st.warning(
        "Tesseract OCR is not installed on this computer. Scanned (image-based) "
        "PDF files cannot be read until it is installed. Digital PDFs and Word "
        "documents still work normally. Please contact your IT support team to "
        "install the OCR component."
    )

with st.sidebar:
    st.header("Load documents")
    markup_file = st.file_uploader("Markup (source)", type=["pdf", "docx"])
    proxy_file = st.file_uploader("Proxy (verify)", type=["pdf", "docx"])
    run = st.button("Compare", type="primary", disabled=not (markup_file and proxy_file))

# Advanced settings are no longer user-facing; the app uses its existing
# defaults/auto-detection internally (unchanged behavior):
#   - document type: auto-detected from the file extension
#   - PDF extraction mode: "auto" (hybrid: digital text, OCR fallback)
#   - comparison granularity: "sentence"
#   - Tesseract: resolved internally (env / PATH / standard install location)
mode = "auto"
segment = "sentence"

if run and markup_file and proxy_file:
    tess = find_tesseract() or ""
    cfg = dict(tesseract_cmd=tess or None, ocr_language="eng", ocr_dpi=300,
               min_chars_for_digital=20, segment_mode=segment)
    m_type = detect_type(markup_file.name)
    p_type = detect_type(proxy_file.name)
    try:
        with st.spinner("Comparing (OCR / DOCX rendering may take a few seconds)..."):
            mb, pb = markup_file.getvalue(), proxy_file.getvalue()
            markup = _extract(mb, markup_file.name, m_type, mode, cfg)
            proxy = _extract(pb, proxy_file.name, p_type, mode, cfg)
            diffs = ComparisonEngine(segment_mode=segment).compare(markup, proxy)

            def _plan(dtype, raw, extracted):
                # Comparison always uses `extracted` (unchanged). This only decides
                # how the side is DISPLAYED.
                if dtype == "docx":
                    pdf = _docx_pdf(raw)
                    if pdf:  # visual, paginated rendering via LibreOffice
                        return dict(mode="pdf", bytes=pdf, pages=_pdf_page_count(pdf),
                                    agnostic=True, rendered=True)
                    return dict(mode="docxtext", bytes=None,  # fallback text view
                                pages=extracted.page_count, agnostic=False, rendered=False)
                return dict(mode="pdf", bytes=raw, pages=extracted.page_count,
                            agnostic=False, rendered=False)

            m_disp = _plan(m_type, mb, markup)
            p_disp = _plan(p_type, pb, proxy)
    except Exception as exc:  # friendly handling for the Tesseract-missing case only
        from pytesseract import TesseractNotFoundError
        if isinstance(exc, TesseractNotFoundError):
            st.error(
                "**This document requires OCR, but Tesseract is not available.**\n\n"
                "The document appears to be a scanned / image-based PDF, which must "
                "be read with the Tesseract OCR engine. Tesseract was not found on "
                "this machine.\n\n"
                "Scanned PDFs cannot be processed without it. Please contact IT to "
                "install the approved Tesseract OCR dependency, then try again. "
                "(Digital PDFs and Word documents do not require Tesseract.)"
            )
            st.stop()
        raise
    st.session_state.results = dict(
        markup=markup, proxy=proxy, diffs=diffs,
        markup_type=m_type, proxy_type=p_type,
        markup_disp=m_disp, proxy_disp=p_disp,
        tess=tess or "", lang="eng",
    )
    st.session_state.page = 0
    st.session_state.diff_idx = 0
    st.session_state.pop("spell", None)  # spell check is per-proxy, opt-in

res = st.session_state.get("results")
if not res:
    st.info("Upload both documents (PDF or DOCX) in the sidebar and click **Compare**.")
    st.stop()

markup, proxy, diffs = res["markup"], res["proxy"], res["diffs"]
m_pages, p_pages = res["markup_disp"]["pages"], res["proxy_disp"]["pages"]
maxp = max(m_pages, p_pages)
page = min(st.session_state.get("page", 0), maxp - 1)
st.session_state.page = page
current = diffs[min(st.session_state.get("diff_idx", 0), len(diffs) - 1)] if diffs else None

if m_pages != p_pages:
    st.warning(f"Page counts differ — Markup: {m_pages} pages, Proxy: {p_pages} "
               f"pages. Pages are shown side-by-side by number and are NOT "
               f"guaranteed to correspond.")

# Difference navigation (Previous / Next only)
if diffs:
    idx = min(st.session_state.get("diff_idx", 0), len(diffs) - 1)
    d1, d2, d3 = st.columns([1, 3, 1])
    if d1.button("◀ Previous difference", disabled=idx <= 0, width='stretch'):
        st.session_state.diff_idx = idx - 1
        st.session_state.page = _page_of(diffs[idx - 1].location)
        st.rerun()
    kind = TYPE_KIND.get(diffs[idx].diff_type, "modified")
    d2.markdown(
        f"<div style='text-align:center;font-weight:600'>Difference {idx + 1} of "
        f"{len(diffs)} — {diffs[idx].location} — {kind}</div>",
        unsafe_allow_html=True,
    )
    if d3.button("Next difference ▶", disabled=idx >= len(diffs) - 1, width='stretch'):
        st.session_state.diff_idx = idx + 1
        st.session_state.page = _page_of(diffs[idx + 1].location)
        st.rerun()
else:
    st.success("No differences found. Documents match.")

# Synchronized page navigation
p1, p2, p3 = st.columns([1, 3, 1])
if p1.button("◀ Prev page", disabled=page <= 0, width='stretch'):
    st.session_state.page = page - 1
    st.rerun()
p2.markdown(
    f"<div style='text-align:center;font-weight:600'>Page {page + 1} / {maxp}</div>",
    unsafe_allow_html=True,
)
if p3.button("Next page ▶", disabled=page >= maxp - 1, width='stretch'):
    st.session_state.page = page + 1
    st.rerun()

# The documents — primary UI
def _type_label(res: dict, side: str) -> str:
    disp = res[f"{side}_disp"]
    if res[f"{side}_type"] == "docx":
        return "DOCX (rendered)" if disp["rendered"] else "DOCX (text view)"
    doc = res[side]
    m = doc.pages[0].method.value if doc.pages else "-"
    return f"PDF ({'OCR' if m == 'ocr' else 'Text Extraction'})"


def _spell_flagged() -> set[str]:
    """Canonical tokens flagged by the last proxy spell-check run (or empty)."""
    return {_canon(d["word"]) for d in st.session_state.get("spell", [])}


def _render_side(col, res: dict, side: str, page: int, current) -> None:
    disp = res[f"{side}_disp"]
    who = "Markup" if side == "markup" else "Proxy"
    col.markdown(f"### {who} — {_type_label(res, side)} · {disp['pages']} pages")
    if page >= disp["pages"]:
        col.info("This document has no page here (fewer pages than the other).")
        return
    diffs = _diffs_for(res, page, disp["agnostic"])
    other_tokens = _other_tok(res, side, page, disp["agnostic"])
    # Purple spell-check overlay: proxy side only, and only after the user ran it.
    flagged = _spell_flagged() if side == "proxy" else set()
    if disp["mode"] == "pdf":
        doc = res[side]
        # Rendered DOCX is digital text; native PDF uses its own per-page method.
        method = ("text" if res[f"{side}_type"] == "docx"
                  else doc.pages[page].method.value)
        words = _word_boxes(disp["bytes"], page, method, VIEW_DPI,
                            res["tess"], res["lang"])
        hmap = _highlight_map([w["text"] for w in words], diffs, side,
                              other_tokens, current)
        boxes = [(words[i]["box"], RGB[k], cur) for i, (k, cur) in hmap.items()]
        boxes += [(w["box"], SPELL_RGB, False)
                  for w in words if _canon(w["text"]) in flagged]
        img = _render(disp["bytes"], page, VIEW_DPI)
        col.image(_highlighted(img, boxes), width='stretch')
    else:  # DOCX text fallback (LibreOffice not installed)
        text = res[side].pages[page].text
        hmap = _highlight_map(text.split(), diffs, side, other_tokens, current)
        for i, w in enumerate(text.split()):
            if _canon(w) in flagged and i not in hmap:
                hmap[i] = ("spell", False)
        col.markdown(_docx_html(text, hmap), unsafe_allow_html=True)
        tables_html = _docx_tables_html(res[side].pages[page].tables)
        if tables_html:
            col.markdown(tables_html, unsafe_allow_html=True)
        if page == 0:
            col.caption("Text view — install LibreOffice for page-accurate "
                        "visual rendering with native table borders.")
    if side == "proxy":
        _spell_ui(col, res)


def _spell_rendered_pages(res: dict) -> dict:
    """Map canon(word) -> 1-based page(s) where the word appears in the DISPLAYED
    proxy. The spell checker runs on extraction pages, but a rendered DOCX is
    repaginated, so the extraction page need not match what the reviewer sees.
    Locating the word in the rendered pages keeps the reported page (and the
    purple highlight) pointing at the actual occurrence."""
    disp = res["proxy_disp"]
    if disp["mode"] != "pdf":
        return {}  # text view shows extraction pages verbatim -> already correct
    proxy = res["proxy"]
    loc: dict = {}
    for p in range(disp["pages"]):
        method = ("text" if res["proxy_type"] == "docx"
                  else proxy.pages[min(p, proxy.page_count - 1)].method.value)
        words = _word_boxes(disp["bytes"], p, method, VIEW_DPI,
                            res["tess"], res["lang"])
        for key in {_canon(w["text"]) for w in words}:
            loc.setdefault(key, []).append(p + 1)
    return loc


def _spell_ui(col, res: dict) -> None:
    """Optional, on-demand proxy spell check (separate from comparison)."""
    if col.button("🔎 Run Spell Check", key="spell_btn"):
        proxy = res["proxy"]
        st.session_state.spell = _spell_check([p.text for p in proxy.pages])
        st.rerun()
    if "spell" in st.session_state:
        issues = st.session_state.spell
        located = _spell_rendered_pages(res)
        col.markdown(f"**Spell Check Complete** · Potential spelling issues: "
                     f"**{len(issues)}** "
                     "<span style='color:#963cc8'>(purple)</span>",
                     unsafe_allow_html=True)
        if issues:
            with col.expander("Potential spelling issues", expanded=False):
                for d in issues:
                    pages = located.get(_canon(d["word"]))
                    where = (", ".join(f"Page {p}" for p in pages)
                             if pages else f"Page {d['page']}")
                    st.markdown(
                        f"- Potential spelling issue — Detected **{d['word']}**, "
                        f"suggested *{d['suggestion']}* ({where})"
                    )
        else:
            col.caption("No potential spelling issues found.")


left, right = st.columns(2)
_render_side(left, res, "markup", page, current)
_render_side(right, res, "proxy", page, current)

# Application footer (custom branding)
st.markdown(
    f"""
    <hr style='margin-top:2rem;border:none;border-top:1px solid #ccc'>
    <div style='text-align:center;color:#888;font-size:0.85rem;padding:8px 0'>
      <strong>{APP_NAME}</strong><br>{APP_TAGLINE}
    </div>
    """,
    unsafe_allow_html=True,
)
