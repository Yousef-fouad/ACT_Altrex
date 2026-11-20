# Validation notes — Assignment 1

These are actual execution results, not descriptions of intended behavior.
Reproduce with:

```bash
uv run --locked marimo check notebooks/assignment_1.py
uv run --locked python notebooks/assignment_1.py
```

## Source inspection (before any transformation)

- **NA workbook / SA workbook** (`Sheet1`, 203 rows × 42 cols each): each
  contains exactly 3 real country rows with 36 monthly date columns
  (2014-01 through 2016-12), surrounded entirely by decorative/decoy cells
  (e.g. `"WASTED SPACE"`, `"USELESS FORMATTING"`, `"Hidden Value - Don't
  Show!!!"`, two decoy `"THE YEAR"` columns labeled 2015/2016 that do not
  align with the real date header row). NA's real countries: United States,
  Mexico, Canada. SA's: Brazil, Chile, Colombia. No other row in either
  sheet contains data (verified by scanning every row for non-blank,
  non-decoy cells).
- **Managers workbook**: three clean sheets — North America (3 rows), Europe
  (4 rows), South America (3 rows). Country text has inconsistent
  leading/trailing whitespace (e.g. `" Canada  "`, `"United States "`). Team
  Size is inconsistently formatted per row: plain integers, `"135 EE"`,
  `"235 Ees"`, `"7 Employees."`, `"team of 15"`, `"10 Persons"`, `"24 Ppl"`.

## Parsing logic

The parser locates the real table structurally instead of hardcoding row/
column numbers: it finds the cell literally equal to `"Country"` (the real
header), and separately finds the row with the most datetime-typed cells
(the real date header — decoy "year" labels are plain integers, not dates,
so they're never mistaken for it). Every row below the Country header with
a non-blank country cell is kept; blank/space-only rows are skipped and
counted, not silently dropped without a record.

This logic was executed twice independently and cross-checked
(`scripts/verify_pipeline.py`, which re-implements the same structural
detection, against a brute-force hardcoded-row-index read of the same three
rows per file) — results matched to the cell:

| Country | Parser sum | Brute-force sum | Match |
| --- | --- | --- | --- |
| United States | 9,790,032.096773291 | 9,790,032.096773291 | ✅ |
| Mexico | 4,902,875.0 | 4,902,875.0 | ✅ |
| Canada | 5,677,825.0 | 5,677,825.0 | ✅ |
| Brazil | 4,709,005.438547953 | 4,709,005.438547953 | ✅ |
| Chile | 797,308.9076047534 | 797,308.9076047534 | ✅ |
| Colombia | 1,763,404.8042891703 | 1,763,404.8042891703 | ✅ |

**Grand total (all 216 expense cells): 27,640,451.247215167** (full
precision, as stored — never rounded).

## Row-count reconciliation

- NA: 3 countries × 36 months = 108 expense cells (0 decoy rows skipped
  below the header, since the structural detector never descends into the
  decoy columns above it).
- SA: 3 countries × 36 months = 108 expense cells.
- Combined `expenses_raw`: **216 rows**. `Detail` report: **216 rows**. No
  rows lost or duplicated going from source → combined → joined → Detail.
- Missing expense values found: **0**. Duplicate (country, date) pairs
  found: **0**.

## Manager matching

- Matched on **Country**, left join, `validate="m:1"` (pandas raises if a
  country ever matched more than one manager row — the structural guarantee
  against the join duplicating expenses).
- All 6 expense countries matched exactly one manager row. 0 unmatched
  expense countries.
- Team Size parsed successfully for all 10 manager rows (regex-extracted
  first integer: `"135 EE"` → 135, `"7 Employees."` → 7, `"team of 15"` →
  15, etc.). 0 parse failures.
- 4 manager rows are **unused references, not unmatched expenses** — the
  entire Europe sheet (Austria, Italy, Spain, United Kingdom) has no
  corresponding expense data in either source workbook, so it is reported
  separately and excluded from the join, not merged in or treated as an
  error.
- No duplicate country values anywhere in the manager reference data.

## Financial controls (all computed from source data, not from the reports)

All 9 controls passed: no missing expense values, no duplicate
(country, date) rows, no duplicate manager countries, all team sizes
parsed, all expense countries matched, Detail row count equals combined
source row count, Detail total / Summary total each reconcile to the
independently-summed source total within `1e-6` (floating-point tolerance
only, not an accounting rounding rule), and every country's source-vs-Detail
subtotal reconciles.

## Export

Ran (`scripts/test_export_logic.py`, against a throwaway temp path):
1. A deliberately failing control blocks export — confirmed no file written.
2. Fresh export with all real controls passing — succeeds.
3. Re-running without confirming overwrite on an existing file — blocked,
   file untouched (mtime unchanged).
4. Re-running with overwrite confirmed — succeeds.
5. Reopened the written workbook from disk (not the in-memory DataFrames)
   and re-verified sheet names, column order, row counts, and totals.

Then performed the one real export for this session
(`scripts/run_real_export.py`, reusing the same validated logic) to
`outputs/assignment_1_draft.xlsx` — **draft only**, not the tracked
submission file. Reopened and reconfirmed:

- Sheets: `Summary by Country`, `Detail` (exact names and order required by
  `assignment.md`).
- `Summary by Country` columns: Country, Manager, `Expense: SUM`,
  `Team Size: MAX` — 6 rows.
- `Detail` columns: Country, Date, Expense, Manager, Team Size — 216 rows.
- Expense columns are formatted `#,##0.00` for display only; the underlying
  stored values retain full source precision (e.g. `9790032.096773291`, not
  `9790032.10`). **A column total you compute from the displayed 2-decimal
  figures in Excel may differ in the last decimal(s) from the stored
  `Expense: SUM` value — this is a display-rounding artifact, not a data
  error.**
- Confirmed running `python notebooks/assignment_1.py` as a script does
  **not** write any file (the export button defaults to unclicked; `ls
  outputs/` before/after is identical).

Running the interactive notebook (`uv run --locked marimo edit
notebooks/assignment_1.py`) and clicking the Export button in the UI
reproduces this same, already-validated code path.

## Policies and unresolved items

- **Currency**: no currency column/label exists anywhere in the three
  source workbooks. No FX conversion was assumed or applied. If NA and SA
  figures are actually denominated in different currencies, that is an
  unresolved question for the instructor — not something this notebook
  decided on its own.
- **Rounding**: none applied to stored values at any stage; only Excel
  display formatting.
- **Original Alteryx output**: not supplied for this assignment, so a
  source-vs-Alteryx-output comparison is **not available**. All
  reconciliation here is source-vs-report only.
- **Deliverable format discrepancy** (see `workflow.md`): the student's
  initial wording asked for two separate downloadable files; `assignment.md`
  requires one workbook with two worksheets. Implemented per `assignment.md`
  (the graded spec), flagged rather than silently decided.
- `submission/assignment_1.xlsx` was copied from the reviewed
  `outputs/assignment_1_draft.xlsx` on 2026-11-19 after the student
  confirmed the draft. Reopened independently and reconfirmed: sheets
  `['Summary by Country', 'Detail']`, shapes `(6, 4)` / `(216, 5)`, same
  column names, Summary total and Detail total both
  `27,640,451.247215167`.
