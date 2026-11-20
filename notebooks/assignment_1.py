import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import re
    from datetime import datetime
    from pathlib import Path

    import marimo as mo
    import numpy as np
    import openpyxl
    import openpyxl.utils
    import pandas as pd

    return Path, datetime, mo, np, openpyxl, pd, re


@app.cell
def _(mo):
    mo.md(r"""
    # Assignment 1 — Consolidated expense report

    Source: North America expenses, South America expenses, and a manager
    reference workbook (`starter_data/`, unchanged). This notebook
    reshapes, combines, and matches those sources into two reports:

    - **Summary by Country** — Country, Manager, Expense: SUM, Team Size: MAX
    - **Detail** — Country, Date, Expense, Manager, Team Size

    Every stage below is its own cell with its own intermediate table so
    each transformation can be inspected before the next one runs.
    """)
    return


@app.cell
def _(mo):
    mo.mermaid(
        """
        flowchart TD
            NA["NA workbook\n(starter_data/*NA.xlsx)"]
            SA["SA workbook\n(starter_data/*SA.xlsx)"]
            MGR["Managers workbook\n(NA / Europe / SA sheets)"]

            NA -->|"parse_expense_workbook\n(drop decoys & blanks)"| NAraw["na_raw\n(country, date, expense)"]
            SA -->|"parse_expense_workbook\n(drop decoys & blanks)"| SAraw["sa_raw\n(country, date, expense)"]
            NAraw -->|Union| COMB["expenses_raw\n(combined long table)"]
            SAraw -->|Union| COMB

            MGR -->|"clean country / manager text\nparse Team Size with regex"| MGRclean["managers\n(cleaned, 1 row per country)"]

            COMB -->|"Join on Country\n(validate 1 manager per country)"| DETAIL["detail_report\nCountry, Date, Expense, Manager, Team Size"]
            MGRclean --> DETAIL

            DETAIL -->|"Summarize\nGroupBy Country+Manager\nSum(Expense), Max(Team Size)"| SUMMARY["summary_report\nCountry, Manager, Expense SUM, Team Size MAX"]

            DETAIL --> CHECKS["Reconciliation controls\n(counts, missing, duplicates,\nunmatched/unused, totals)"]
            SUMMARY --> CHECKS
            CHECKS -->|"all controls pass\n+ intentional button click"| EXPORT["outputs/assignment_1_draft.xlsx\n(Summary by Country + Detail sheets)"]
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Note on this diagram vs. Marimo's real dependency graph:** this
    mermaid diagram is hand-drawn to communicate the workflow; it is not
    proof that the code actually runs this way. Marimo tracks the *real*
    variable dependencies between cells automatically — open the
    dependency graph from the panel on the left of the Marimo editor (the
    graph/network icon) while running `uv run --locked marimo edit
    notebooks/assignment_1.py` to see which cells truly depend on which
    variables. If the two ever disagree, trust the dependency graph, not
    this picture.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Assumptions and policies (stated up front, not invented later)

    - **Currency:** none of the three workbooks contains a currency
      column or label. No FX conversion is applied — amounts are combined
      as given. If NA and SA amounts are actually in different
      currencies, that is a material question for the instructor, not an
      assumption this notebook makes silently.
    - **Rounding:** source precision is preserved end to end. Amounts are
      never rounded in storage; Excel number formatting (`#,##0.00`) is
      applied only for *display* in the exported workbook.
    - **Tolerance:** reconciliation checks that compare sums use an
      absolute tolerance of `1e-6` to absorb binary floating-point
      representation error only — this is not an accounting rounding
      rule.
    - **Missing/duplicate data:** missing expense amounts are never
      replaced with zero, and unmatched/duplicate rows are never silently
      dropped. Both are surfaced as explicit exception tables below.
    """)
    return


@app.cell
def _(Path, mo):
    _nb_dir = mo.notebook_dir()
    repo_root = _nb_dir.parent if _nb_dir is not None else Path.cwd()

    na_path = repo_root / "starter_data" / "Automation Build Challenge - NA.xlsx"
    sa_path = repo_root / "starter_data" / "Automation Build Challenge - SA.xlsx"
    managers_path = (
        repo_root / "starter_data" / "Automation Build Challenge - Managers.xlsx"
    )

    mo.md(
        f"""
        **Resolved paths** (relative to the repository root, regardless of
        where the notebook process is launched from):

        - `{na_path.relative_to(repo_root)}`
        - `{sa_path.relative_to(repo_root)}`
        - `{managers_path.relative_to(repo_root)}`
        """
    )
    return managers_path, na_path, repo_root, sa_path


@app.cell
def _(mo):
    mo.md(r"""
    ## Stage 1 — Identify the real tables, drop decoys (Alteryx: Filter + Select)

    Both country workbooks are intentionally messy: stray labels like
    *"WASTED SPACE"*, *"USELESS FORMATTING"*, *"Hidden Value - Don't
    Show!!!"*, and decoy *"THE YEAR"* columns sit around the real data.
    Rather than hardcoding row/column numbers (which would silently break
    if the decoys moved), the parser below locates the real table
    structurally:

    - the header row containing the literal cell **"Country"**,
    - the row with the most datetime-typed cells (the real monthly date
      header — decoy cells like the "2015"/"2016" labels are plain
      integers, not dates, so they are never picked up), and
    - every row below the "Country" header whose country cell is a
      non-blank string (blank/space-only separator rows are skipped and
      counted).

    This is the Python equivalent of an Alteryx **Filter** tool (dropping
    non-data rows) followed by a **Select** (keeping only the real
    columns).
    """)
    return


@app.cell
def _(datetime, openpyxl, pd):
    def parse_expense_workbook(path, source_label):
        """Extract the (country, date, expense) table from a decoy-laden
        monthly-expense workbook, without assuming fixed row/column numbers."""
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb[wb.sheetnames[0]]
        rows = list(ws.iter_rows(values_only=True))

        country_col = None
        country_header_row = None
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                if isinstance(val, str) and val.strip() == "Country":
                    country_col, country_header_row = c_idx, r_idx
                    break
            if country_col is not None:
                break
        if country_col is None:
            raise ValueError(f"No 'Country' header cell found in {path.name}")

        date_row_idx, date_cols = None, []
        for r_idx, row in enumerate(rows):
            dt_cols = [c for c, val in enumerate(row) if isinstance(val, datetime)]
            if len(dt_cols) > len(date_cols):
                date_row_idx, date_cols = r_idx, dt_cols
        if not date_cols:
            raise ValueError(f"No monthly date header row found in {path.name}")
        dates = {c: rows[date_row_idx][c] for c in date_cols}

        records = []
        skipped_blank_rows = 0
        for r_idx in range(country_header_row + 1, len(rows)):
            raw_country = rows[r_idx][country_col]
            is_blank = raw_country is None or (
                isinstance(raw_country, str) and raw_country.strip() == ""
            )
            if is_blank:
                skipped_blank_rows += 1
                continue
            country = raw_country.strip() if isinstance(raw_country, str) else raw_country
            for c_idx, dt in dates.items():
                records.append(
                    {
                        "country_raw": raw_country,
                        "country": country,
                        "date": dt,
                        "expense": rows[r_idx][c_idx],
                        "source_file": source_label,
                        "source_row": r_idx + 1,
                    }
                )

        df = pd.DataFrame.from_records(
            records,
            columns=["country_raw", "country", "date", "expense", "source_file", "source_row"],
        )
        meta = {
            "source_file": source_label,
            "n_countries": df["country"].nunique() if not df.empty else 0,
            "n_date_columns": len(date_cols),
            "n_expense_cells": len(df),
            "skipped_blank_rows": skipped_blank_rows,
        }
        return df, meta

    return (parse_expense_workbook,)


@app.cell
def _(na_path, parse_expense_workbook, sa_path):
    na_raw, na_meta = parse_expense_workbook(na_path, "NA")
    sa_raw, sa_meta = parse_expense_workbook(sa_path, "SA")
    return na_meta, na_raw, sa_meta, sa_raw


@app.cell
def _(mo, na_meta, na_raw, sa_meta, sa_raw):
    mo.vstack(
        [
            mo.md(
                f"""
                **Parsed structure:**

                - NA: {na_meta["n_countries"]} countries ×
                  {na_meta["n_date_columns"]} months =
                  {na_meta["n_expense_cells"]} expense cells
                  ({na_meta["skipped_blank_rows"]} decoy/blank rows skipped)
                - SA: {sa_meta["n_countries"]} countries ×
                  {sa_meta["n_date_columns"]} months =
                  {sa_meta["n_expense_cells"]} expense cells
                  ({sa_meta["skipped_blank_rows"]} decoy/blank rows skipped)
                """
            ),
            mo.ui.table(na_raw, label="na_raw (North America, long format)", page_size=10),
            mo.ui.table(sa_raw, label="sa_raw (South America, long format)", page_size=10),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Stage 2 — Restructure to rows and combine (Alteryx: Transpose + Union)

    Each workbook is already produced in long/tidy form by the parser
    above (one row per country-month cell), which is exactly what an
    Alteryx **Transpose** tool does to wide monthly columns. The two
    country tables are then stacked with an Alteryx **Union**-equivalent
    (`pandas.concat`). Missing expense values and duplicate
    (country, date) pairs are flagged here — not dropped or zero-filled.
    """)
    return


@app.cell
def _(na_raw, pd, sa_raw):
    expenses_raw = pd.concat([na_raw, sa_raw], ignore_index=True)

    missing_expense_rows = expenses_raw[expenses_raw["expense"].isna()]
    duplicate_country_date_rows = expenses_raw[
        expenses_raw.duplicated(subset=["country", "date"], keep=False)
    ]
    return duplicate_country_date_rows, expenses_raw, missing_expense_rows


@app.cell
def _(duplicate_country_date_rows, expenses_raw, missing_expense_rows, mo):
    mo.vstack(
        [
            mo.md(
                f"""
                **Combined long table:** {len(expenses_raw)} rows
                ({expenses_raw["country"].nunique()} countries).
                Missing expense values: **{len(missing_expense_rows)}**.
                Duplicate (country, date) pairs: **{len(duplicate_country_date_rows)}**.
                """
            ),
            mo.ui.table(expenses_raw, label="expenses_raw (combined NA + SA)", page_size=10),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Stage 3 — Clean manager information (Alteryx: Data Cleansing + RegEx)

    The Managers workbook has no decoys — each of its three sheets
    (North America, Europe, South America) is already a clean table — but
    country/manager text has stray leading/trailing whitespace, and
    **Team Size** is inconsistently formatted (`"135 EE"`, `"7
    Employees."`, `"team of 15"`, plain integers, ...). Text is trimmed
    and the first integer found in each Team Size cell is extracted with
    a regular expression (Alteryx's **RegEx** tool, parse mode). Cells
    where no digits are found are flagged rather than silently coerced.
    """)
    return


@app.cell
def _(managers_path, np, pd, re):
    def _extract_team_size(value):
        if isinstance(value, (int, float)) and not pd.isna(value):
            return float(value)
        match = re.search(r"\d+", str(value))
        return float(match.group()) if match else np.nan

    _sheets = pd.read_excel(managers_path, sheet_name=None)
    _frames = []
    for _sheet_name, _df in _sheets.items():
        _d = _df.copy()
        _d["source_sheet"] = _sheet_name
        _frames.append(_d)
    managers_raw = pd.concat(_frames, ignore_index=True)

    managers = managers_raw.copy()
    managers["country"] = managers["Country"].astype(str).str.strip()
    managers["manager"] = managers["Manager"].astype(str).str.strip()
    managers["team_size_raw"] = managers["Team Size"]
    managers["team_size"] = managers["team_size_raw"].apply(_extract_team_size)

    team_size_unparsed = managers[managers["team_size"].isna()]
    return managers, managers_raw, team_size_unparsed


@app.cell
def _(managers, managers_raw, mo, team_size_unparsed):
    mo.vstack(
        [
            mo.md(
                f"""
                **Managers cleaned:** {len(managers)} reference rows across
                {managers_raw["source_sheet"].nunique()} sheets
                ({", ".join(managers_raw["source_sheet"].unique())}).
                Team Size cells that failed to parse to a number:
                **{len(team_size_unparsed)}**.
                """
            ),
            mo.ui.table(managers_raw, label="managers_raw (as read, all sheets)", page_size=8),
            mo.ui.table(
                managers[["country", "manager", "team_size_raw", "team_size", "source_sheet"]],
                label="managers (cleaned)",
                page_size=8,
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Stage 4 — Match expenses to managers (Alteryx: Join on Country)

    Expenses are joined to the cleaned manager reference on **Country**,
    a left join (`validate="m:1"`) so every expense row is kept even if
    unmatched, and pandas itself raises if any country were to match more
    than one manager row (it would mean the join could duplicate
    expenses — the equivalent of checking an Alteryx Join's cardinality).
    Unused reference rows (countries in the Managers workbook with no
    expense data — expected for the whole Europe sheet) are reported
    separately from any unmatched *expense* countries, which would be a
    real problem.
    """)
    return


@app.cell
def _(expenses_raw, managers):
    expense_countries = set(expenses_raw["country"].unique())
    manager_countries = set(managers["country"].unique())

    unmatched_expense_countries = sorted(expense_countries - manager_countries)
    unused_manager_rows = managers[~managers["country"].isin(expense_countries)]
    duplicate_manager_countries = managers[
        managers.duplicated(subset=["country"], keep=False)
    ]

    detail_joined = expenses_raw.merge(
        managers[["country", "manager", "team_size"]],
        on="country",
        how="left",
        validate="m:1",
    )
    return (
        detail_joined,
        duplicate_manager_countries,
        unmatched_expense_countries,
        unused_manager_rows,
    )


@app.cell
def _(
    detail_joined,
    duplicate_manager_countries,
    mo,
    pd,
    unmatched_expense_countries,
    unused_manager_rows,
):
    unmatched_after_join = detail_joined[detail_joined["manager"].isna()]
    mo.vstack(
        [
            mo.md(
                f"""
                **Matching results:**

                - Unmatched expense countries (no manager found): **{unmatched_expense_countries or "none"}**
                - Expense rows left unmatched after the join: **{len(unmatched_after_join)}**
                - Unused manager reference rows (manager has no expenses — expected for Europe): **{len(unused_manager_rows)}**
                - Manager countries listed more than once (would risk duplicating expenses): **{len(duplicate_manager_countries)}**
                """
            ),
            mo.ui.table(
                unused_manager_rows[["country", "manager", "source_sheet"]]
                if not unused_manager_rows.empty
                else pd.DataFrame(columns=["country", "manager", "source_sheet"]),
                label="unused_manager_rows",
                page_size=6,
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Stage 5 — Build the two reports (Alteryx: Select + Summarize)

    **Detail** is the joined table narrowed and renamed to the required
    columns (Alteryx **Select**). **Summary by Country** groups Detail by
    Country + Manager and aggregates Expense with **Sum** and Team Size
    with **Max** (Alteryx **Summarize**).
    """)
    return


@app.cell
def _(detail_joined):
    detail_report = (
        detail_joined[["country", "date", "expense", "manager", "team_size"]]
        .rename(
            columns={
                "country": "Country",
                "date": "Date",
                "expense": "Expense",
                "manager": "Manager",
                "team_size": "Team Size",
            }
        )
        .sort_values(["Country", "Date"])
        .reset_index(drop=True)
    )

    summary_report = (
        detail_report.groupby(["Country", "Manager"], as_index=False, dropna=False)
        .agg(**{"Expense: SUM": ("Expense", "sum"), "Team Size: MAX": ("Team Size", "max")})
        .sort_values("Country")
        .reset_index(drop=True)
    )
    return detail_report, summary_report


@app.cell
def _(detail_report, mo, summary_report):
    mo.vstack(
        [
            mo.ui.table(summary_report, label="summary_report — Summary by Country", page_size=10),
            mo.ui.table(detail_report, label="detail_report — Detail", page_size=10),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Stage 6 — Financial reconciliation controls

    Every check below is derived **independently from the source data**
    (`expenses_raw`, `managers`), never from the final reports
    themselves, so a bug that corrupts a report cannot also make its own
    check pass. Export is gated on every one of these passing.

    No original Alteryx output was supplied for this assignment, so a
    source-vs-Alteryx-output comparison is **not available** — totals are
    instead reconciled against the parsed source workbooks.
    """)
    return


@app.cell
def _(
    detail_report,
    duplicate_country_date_rows,
    duplicate_manager_countries,
    expenses_raw,
    missing_expense_rows,
    summary_report,
    team_size_unparsed,
    unmatched_expense_countries,
):
    TOLERANCE = 1e-6

    source_total = expenses_raw["expense"].sum()
    detail_total = detail_report["Expense"].sum()
    summary_total = summary_report["Expense: SUM"].sum()

    country_level_check = (
        expenses_raw.groupby("country")["expense"]
        .sum()
        .rename("source_total")
        .to_frame()
        .join(detail_report.groupby("Country")["Expense"].sum().rename("detail_total"))
    )
    country_level_check["difference"] = (
        country_level_check["source_total"] - country_level_check["detail_total"]
    )

    controls = {
        "no_missing_expense_values": len(missing_expense_rows) == 0,
        "no_duplicate_country_date_rows": len(duplicate_country_date_rows) == 0,
        "no_duplicate_manager_countries": len(duplicate_manager_countries) == 0,
        "all_team_sizes_parsed": len(team_size_unparsed) == 0,
        "all_expense_countries_matched": len(unmatched_expense_countries) == 0,
        "detail_row_count_matches_source": len(detail_report) == len(expenses_raw),
        "detail_total_matches_source_total": abs(detail_total - source_total) < TOLERANCE,
        "summary_total_matches_source_total": abs(summary_total - source_total) < TOLERANCE,
        "country_level_totals_reconcile": bool(
            (country_level_check["difference"].abs() < TOLERANCE).all()
        ),
    }
    all_controls_passed = all(controls.values())
    return all_controls_passed, controls, country_level_check


@app.cell
def _(all_controls_passed, controls, country_level_check, mo):
    _lines = "\n".join(
        f"- {'✅' if passed else '❌'} `{name}`" for name, passed in controls.items()
    )
    mo.vstack(
        [
            mo.md(
                f"""
                {_lines}

                **All controls passed: {"✅ yes — export is unblocked" if all_controls_passed else "❌ no — export stays blocked"}**
                """
            ),
            mo.ui.table(country_level_check.reset_index(), label="country_level_check", page_size=10),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Stage 7 — Intentional export (Alteryx: Output Data)

    Export only runs when the button below is clicked (its value is
    `False` on load and when this file is run as a plain script, so
    nothing is written on startup or on routine reactive recalculation).
    It is also blocked unless every control above passes, and it will not
    silently overwrite an existing draft — check the confirmation box
    first.
    """)
    return


@app.cell
def _(mo, repo_root):
    output_path = repo_root / "outputs" / "assignment_1_draft.xlsx"
    overwrite_confirm = mo.ui.checkbox(label="Overwrite existing draft if present")
    export_button = mo.ui.run_button(label="Export draft workbook (Summary + Detail)")
    return export_button, output_path, overwrite_confirm


@app.cell
def _(export_button, mo, output_path, overwrite_confirm):
    mo.vstack(
        [
            mo.md(f"Draft export target: `{output_path}`"),
            overwrite_confirm,
            export_button,
        ]
    )
    return


@app.cell
def _(
    all_controls_passed,
    controls,
    detail_report,
    export_button,
    mo,
    openpyxl,
    output_path,
    overwrite_confirm,
    pd,
    summary_report,
):
    mo.stop(
        not export_button.value,
        mo.md("*(Export not run yet — click the button above when ready.)*"),
    )

    if not all_controls_passed:
        _failed = [name for name, passed in controls.items() if not passed]
        export_result = mo.md(f"❌ **Export blocked.** Failing controls: {_failed}")
    elif output_path.exists() and not overwrite_confirm.value:
        export_result = mo.md(
            f"⚠️ `{output_path.name}` already exists. Check **Overwrite existing "
            "draft if present** above and click Export again to replace it."
        )
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(output_path, engine="openpyxl", mode="w") as writer:
            summary_report.to_excel(writer, sheet_name="Summary by Country", index=False)
            detail_report.to_excel(writer, sheet_name="Detail", index=False)

            _currency_format = "#,##0.00"
            _summary_col = openpyxl.utils.get_column_letter(
                summary_report.columns.get_loc("Expense: SUM") + 1
            )
            _detail_col = openpyxl.utils.get_column_letter(
                detail_report.columns.get_loc("Expense") + 1
            )
            _summary_ws = writer.sheets["Summary by Country"]
            _detail_ws = writer.sheets["Detail"]
            for _row in range(2, len(summary_report) + 2):
                _summary_ws[f"{_summary_col}{_row}"].number_format = _currency_format
            for _row in range(2, len(detail_report) + 2):
                _detail_ws[f"{_detail_col}{_row}"].number_format = _currency_format

        export_result = mo.md(f"✅ Exported to `{output_path}`.")

    export_result
    return (export_result,)


@app.cell
def _(detail_report, export_result, mo, output_path, pd, summary_report):
    mo.stop(
        not output_path.exists(),
        mo.md("*(Nothing to verify yet — no draft workbook has been exported.)*"),
    )

    _reopened = pd.read_excel(output_path, sheet_name=None)
    _expected_sheets = ["Summary by Country", "Detail"]
    _checks = {
        "sheets_present": list(_reopened.keys()) == _expected_sheets,
        "summary_columns_match": list(_reopened["Summary by Country"].columns)
        == list(summary_report.columns),
        "detail_columns_match": list(_reopened["Detail"].columns) == list(detail_report.columns),
        "summary_row_count_matches": len(_reopened["Summary by Country"]) == len(summary_report),
        "detail_row_count_matches": len(_reopened["Detail"]) == len(detail_report),
        "summary_total_matches": abs(
            _reopened["Summary by Country"]["Expense: SUM"].sum()
            - summary_report["Expense: SUM"].sum()
        )
        < 1e-6,
        "detail_total_matches": abs(
            _reopened["Detail"]["Expense"].sum() - detail_report["Expense"].sum()
        )
        < 1e-6,
    }
    _lines = "\n".join(f"- {'✅' if ok else '❌'} `{name}`" for name, ok in _checks.items())
    verification_result = mo.md(
        f"""
        **Reopened-workbook verification** (using `{export_result}` as the
        signal that export just ran, then reading `{output_path.name}` back
        from disk independently of the in-memory DataFrames):

        {_lines}
        """
    )
    verification_result
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ### Running this notebook

    - `uv run --locked marimo edit notebooks/assignment_1.py` — interactive editing; use the dependency-graph panel to confirm real cell dependencies.
    - `uv run --locked marimo check notebooks/assignment_1.py` — static checks.
    - `uv run --locked python notebooks/assignment_1.py` — runs the whole notebook as a script; the export button defaults to unclicked, so **no file is written**.

    Once you've reviewed the draft in `outputs/assignment_1_draft.xlsx`,
    copy it to `submission/assignment_1.xlsx` yourself (or ask the
    assistant to do that copy as its own explicit step) — that final copy
    is a separate, deliberate action, not part of this notebook's export.
    """)
    return


if __name__ == "__main__":
    app.run()
