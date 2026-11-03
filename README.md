# PDF QC Comparison Tool

Compares a **Markup** document (source of truth) against a **Proxy** document
(to verify) and produces a QC report of missing, additional and changed content
— including changed values, dates, percentages and table cells.

Supported document types (any combination): **PDF ↔ PDF, DOCX ↔ PDF,
PDF ↔ DOCX, DOCX ↔ DOCX**. All types flow through the same extraction model and
the same comparison engine.

Runs **fully locally**. No cloud APIs, no AI/LLM services.

## Technology & Third-Party Components

The **PDF QC Comparison Tool** — *Local Enterprise Document QC Application* — is
built on open-source components, used unmodified. Full attribution, versions and
licenses are in [`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt).

| Component | Version | Role | License |
| --- | --- | --- | --- |
| Streamlit | 1.63.0 | Review UI | Apache-2.0 |
| pdfplumber | 0.11.10 | PDF text/table extraction, page render | MIT |
| pdfminer.six | 20260107 | PDF parsing (via pdfplumber) | MIT |
| pytesseract | 0.3.13 | OCR wrapper | Apache-2.0 |
| python-docx | 1.2.0 | DOCX extraction | MIT |
| Pillow | 12.3.0 | Image handling | HPND (MIT-CMU) |
| pyspellchecker | 0.9.0 | Proxy spell check (optional) | MIT |
| Tesseract OCR | host (5.5.x) | OCR engine (external) | Apache-2.0 |
| LibreOffice | host (optional) | DOCX→PDF render (external) | MPL-2.0 |

External components (Tesseract, LibreOffice) are invoked as separate local
executables — not bundled, not modified. Streamlit's own menu/footer branding is
adjusted only through officially supported configuration (page config, About
menu, CSS) — the Streamlit package itself is never patched.

## Environment Setup

Recreate the environment on a fresh machine:

```bash
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt          # runtime (CLI + UI)
pip install -r requirements-dev.txt       # optional: adds pytest for tests
```

Runtime dependencies (pinned in `requirements.txt`): `pdfplumber`, `pytesseract`,
`Pillow`, `python-docx`, and `streamlit` (UI only).

OCR (for scanned PDFs) also requires the **Tesseract** engine installed on the
machine — it is a system binary, not a pip package:

- Windows: install the Tesseract binary and either add it to `PATH` or pass
  `--tesseract "C:\Program Files\Tesseract-OCR\tesseract.exe"`.
- Digital-only PDFs and DOCX files do not need Tesseract.

**Optional — LibreOffice** (visual DOCX rendering in the UI). To display DOCX
files as real, laid-out pages side-by-side with PDFs, install LibreOffice
locally (`soffice` on PATH, or the default `C:\Program Files\LibreOffice`). It is
a local system dependency — nothing is uploaded, no AI/cloud. Without it the UI
falls back to a paginated text view of the DOCX. Not needed for the CLI.

## Usage

```bash
python -m pdfqc markup.pdf proxy.pdf -o report.md
```

Document type is auto-detected from the extension; `.docx` is also accepted:

```bash
python -m pdfqc markup.docx proxy.pdf -o report.md
```

Options:

- `-o, --out` – write the Markdown report to a file (otherwise printed).
- `-m, --mode` – PDF extraction mode: `auto` (default, hybrid), `text`, or `ocr`
  (ignored for DOCX).
- `--markup-type` / `--proxy-type` – `auto` (default), `pdf`, or `docx`.
- `--segment` – `sentence` (default) or `line` comparison granularity.
- `--tesseract` – path to the Tesseract executable.
- `--dpi` – OCR rasterization DPI (default 300).
- `--lang` – Tesseract language (default `eng`).

## Validation UI (Streamlit)

A local, validation-focused UI for reviewing extraction and comparison output.

```bash
pip install -r requirements-dev.txt
python -m streamlit run app.py
```

Then open the printed `http://localhost:8501`. Upload the Markup and Proxy
documents (PDF or DOCX), pick each type (Auto / PDF / Word) or leave on Auto,
and click **Compare**. The documents are the primary interface (UI only —
reuses the pipeline unchanged):

- Detected type shown per side (e.g. `PDF (Text Extraction)`, `DOCX (rendered)`).
- Both documents rendered side-by-side with **differences highlighted**:
  yellow = modified, red = missing from proxy, blue = additional in proxy.
- **DOCX viewer:** with LibreOffice installed, DOCX is converted to a laid-out
  PDF and shown as real paginated pages (`DOCX (rendered)`) with box highlights,
  synchronized page-by-page with the other document. Without LibreOffice it
  falls back to a paginated text view (`DOCX (text view)`).
- If the two documents have different page counts, a warning is shown and pages
  are not assumed to correspond.
- **Synchronized** page navigation (both viewers stay on the same page).
- **Previous / Next difference** controls that jump to the relevant page and
  outline the current difference.

PDF (and rendered-DOCX) highlight locations use `pdfplumber` word coordinates
(digital) and Tesseract word boxes (OCR); DOCX text-view highlights wrap changed
words in the rendered text. All approximate; resolved in the UI layer.

### How DOCX rendering works (and why it is separate)

DOCX has no PDF-style page boundaries in its XML, so paragraphs ≠ pages. For a
faithful visual, the UI converts DOCX → PDF with **LibreOffice headless**
(`pdfqc/rendering/docx_renderer.py`) and reuses the existing PDF page renderer.
This is display-only: the comparison engine keeps consuming the unchanged
`WordExtractor` output, so extraction/comparison stay document-type agnostic.

Detection (`find_soffice`): checks `soffice`/`libreoffice` on `PATH`, then the
common Windows install paths (`C:\Program Files\LibreOffice\program\soffice.exe`
and the x86 variant). No per-user path is hardcoded.

Known limitation: rendered (layout) pages need not match the extraction pages
that diffs are numbered by, so highlights on a rendered DOCX are located by text
match across pages (page-level association), which can highlight a repeated
changed token on more than one page.

### Proxy spell check (optional)

A separate, opt-in check that runs **only on the Proxy** — it never touches the
Markup or the comparison results. In the UI, click **🔎 Run Spell Check** under
the Proxy viewer; potential issues are highlighted in **purple** (distinct from
the comparison colors) and listed with a suggestion and page number. Wording is
deliberately "potential spelling issue", not "error".

It is tuned for **low false positives** on scanned/OCR proxies: only plain
lowercase words (length ≥ 4) with a single-edit correction are flagged; numbers,
currency, dates, percentages, URLs, emails, tickers, acronyms, hyphenated terms,
proper nouns and OCR garbage are skipped. Add known-good terms to
[`custom_dictionary.txt`](custom_dictionary.txt) (one per line) — no code change
needed. Uses `pyspellchecker` (local, offline; no AI/cloud).

### Testing DOCX ↔ PDF

```bash
python -m streamlit run app.py
```

Upload `samples/sample_markup_3page.docx` as Markup and any PDF as Proxy (or a
second DOCX). With LibreOffice installed the DOCX shows as real pages; use
Prev/Next page to step DOCX Page N ↔ PDF Page N. `pytest -q` runs the automated
checks (the real DOCX→PDF conversion test runs only when LibreOffice is present).

## Run tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Layout

```
pdfqc/
  config.py            # Config dataclass
  models.py            # PageContent, ExtractionResult, Difference, QCReport
  extractors/          # TextExtractor, OCRExtractor, HybridExtractor
  normalizers/         # text normalization + segmentation
  comparators/         # ComparisonEngine (difflib-based)
  reports/             # ReportGenerator (Markdown)
  cli.py               # command-line entry point
tests/                 # pytest suite
```

See `TECHNICAL_DESIGN.md`, `AI_HANDOFF.md`, `IMPLEMENTATION_PROGRESS.md`.
