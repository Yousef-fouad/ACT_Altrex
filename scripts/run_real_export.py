"""Perform the one real, intentional export this session — reusing the exact
logic validated in test_export_logic.py, with real (not fake) controls,
against the real outputs/assignment_1_draft.xlsx destination. This is the
headless equivalent of clicking the notebook's export button, used only
because the notebook's run_button can't be clicked outside the Marimo UI.
"""
import re
import sys
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from verify_pipeline import parse_expense_workbook  # noqa: E402


def main():
    na = parse_expense_workbook(REPO_ROOT / "starter_data/Automation Build Challenge - NA.xlsx", "NA")
    sa = parse_expense_workbook(REPO_ROOT / "starter_data/Automation Build Challenge - SA.xlsx", "SA")
    expenses_raw = pd.concat([na, sa], ignore_index=True)

    managers = pd.concat(
        [df.assign(source_sheet=name) for name, df in pd.read_excel(
            REPO_ROOT / "starter_data/Automation Build Challenge - Managers.xlsx", sheet_name=None
        ).items()],
        ignore_index=True,
    )
    managers["country"] = managers["Country"].astype(str).str.strip()
    managers["manager"] = managers["Manager"].astype(str).str.strip()

    def extract_team_size(v):
        if isinstance(v, (int, float)) and not pd.isna(v):
            return float(v)
        m = re.search(r"\d+", str(v))
        return float(m.group()) if m else np.nan

    managers["team_size"] = managers["Team Size"].apply(extract_team_size)

    missing_expense_rows = expenses_raw[expenses_raw["expense"].isna()]
    duplicate_country_date_rows = expenses_raw[expenses_raw.duplicated(subset=["country", "date"], keep=False)]
    team_size_unparsed = managers[managers["team_size"].isna()]
    duplicate_manager_countries = managers[managers.duplicated(subset=["country"], keep=False)]

    expense_countries = set(expenses_raw["country"].unique())
    manager_countries = set(managers["country"].unique())
    unmatched_expense_countries = sorted(expense_countries - manager_countries)

    detail_joined = expenses_raw.merge(
        managers[["country", "manager", "team_size"]], on="country", how="left", validate="m:1"
    )
    detail_report = (
        detail_joined[["country", "date", "expense", "manager", "team_size"]]
        .rename(columns={"country": "Country", "date": "Date", "expense": "Expense", "manager": "Manager", "team_size": "Team Size"})
        .sort_values(["Country", "Date"])
        .reset_index(drop=True)
    )
    summary_report = (
        detail_report.groupby(["Country", "Manager"], as_index=False)
        .agg(**{"Expense: SUM": ("Expense", "sum"), "Team Size: MAX": ("Team Size", "max")})
        .sort_values("Country")
        .reset_index(drop=True)
    )

    TOLERANCE = 1e-6
    source_total = expenses_raw["expense"].sum()
    detail_total = detail_report["Expense"].sum()
    summary_total = summary_report["Expense: SUM"].sum()
    country_level_check = (
        expenses_raw.groupby("country")["expense"].sum().rename("source_total").to_frame()
        .join(detail_report.groupby("Country")["Expense"].sum().rename("detail_total"))
    )
    country_level_check["difference"] = country_level_check["source_total"] - country_level_check["detail_total"]

    controls = {
        "no_missing_expense_values": len(missing_expense_rows) == 0,
        "no_duplicate_country_date_rows": len(duplicate_country_date_rows) == 0,
        "no_duplicate_manager_countries": len(duplicate_manager_countries) == 0,
        "all_team_sizes_parsed": len(team_size_unparsed) == 0,
        "all_expense_countries_matched": len(unmatched_expense_countries) == 0,
        "detail_row_count_matches_source": len(detail_report) == len(expenses_raw),
        "detail_total_matches_source_total": abs(detail_total - source_total) < TOLERANCE,
        "summary_total_matches_source_total": abs(summary_total - source_total) < TOLERANCE,
        "country_level_totals_reconcile": bool((country_level_check["difference"].abs() < TOLERANCE).all()),
    }
    all_controls_passed = all(controls.values())
    print("Controls:", controls)
    print("All controls passed:", all_controls_passed)
    if not all_controls_passed:
        print("REFUSING TO EXPORT: a control failed.")
        return 1

    output_path = REPO_ROOT / "outputs" / "assignment_1_draft.xlsx"
    if output_path.exists():
        print(f"REFUSING TO EXPORT: {output_path} already exists and no overwrite was confirmed.")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl", mode="w") as writer:
        summary_report.to_excel(writer, sheet_name="Summary by Country", index=False)
        detail_report.to_excel(writer, sheet_name="Detail", index=False)
        currency_format = "#,##0.00"
        summary_col = openpyxl.utils.get_column_letter(summary_report.columns.get_loc("Expense: SUM") + 1)
        detail_col = openpyxl.utils.get_column_letter(detail_report.columns.get_loc("Expense") + 1)
        summary_ws = writer.sheets["Summary by Country"]
        detail_ws = writer.sheets["Detail"]
        for row in range(2, len(summary_report) + 2):
            summary_ws[f"{summary_col}{row}"].number_format = currency_format
        for row in range(2, len(detail_report) + 2):
            detail_ws[f"{detail_col}{row}"].number_format = currency_format

    print(f"EXPORTED: {output_path}")

    # Reopen and verify, exactly like the notebook's verification cell.
    reopened = pd.read_excel(output_path, sheet_name=None)
    assert list(reopened.keys()) == ["Summary by Country", "Detail"]
    assert list(reopened["Summary by Country"].columns) == list(summary_report.columns)
    assert list(reopened["Detail"].columns) == list(detail_report.columns)
    assert len(reopened["Detail"]) == len(detail_report)
    assert len(reopened["Summary by Country"]) == len(summary_report)
    assert abs(reopened["Detail"]["Expense"].sum() - detail_report["Expense"].sum()) < TOLERANCE
    assert abs(reopened["Summary by Country"]["Expense: SUM"].sum() - summary_report["Expense: SUM"].sum()) < TOLERANCE
    print("Reopened-workbook verification: OK")
    print("\nSummary by Country:")
    print(summary_report.to_string(index=False))
    print(f"\nDetail rows: {len(detail_report)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
