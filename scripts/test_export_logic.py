"""Exercise the notebook's export-gating logic outside Marimo's UI runtime,
since a run_button's value can't be set headlessly. Reproduces the exact
branch logic from the export cell in notebooks/assignment_1.py against a
throwaway temp file, covering: a failing control, a fresh export, a blocked
re-export (no overwrite confirmation), and a confirmed overwrite.
"""
import shutil
import sys
import tempfile
from pathlib import Path

import openpyxl
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from verify_pipeline import parse_expense_workbook  # noqa: E402


def build_reports():
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
    import re
    import numpy as np

    def extract_team_size(v):
        if isinstance(v, (int, float)) and not pd.isna(v):
            return float(v)
        m = re.search(r"\d+", str(v))
        return float(m.group()) if m else np.nan

    managers["team_size"] = managers["Team Size"].apply(extract_team_size)

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
    return summary_report, detail_report


def do_export(output_path, overwrite_confirm, all_controls_passed, controls, summary_report, detail_report):
    """Mirrors the export cell's branch logic exactly."""
    if not all_controls_passed:
        failed = [name for name, passed in controls.items() if not passed]
        return f"BLOCKED: failing controls {failed}"
    if output_path.exists() and not overwrite_confirm:
        return "BLOCKED: exists, no overwrite confirmation"

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
    return f"EXPORTED to {output_path}"


def main():
    summary_report, detail_report = build_reports()
    tmp_dir = Path(tempfile.mkdtemp(prefix="act_altrex_export_test_"))
    try:
        output_path = tmp_dir / "test_draft.xlsx"

        # 1. Failing control blocks export, even though the file doesn't exist.
        fake_controls = {"some_check": False, "other_check": True}
        result = do_export(output_path, False, False, fake_controls, summary_report, detail_report)
        assert result.startswith("BLOCKED: failing controls"), result
        assert not output_path.exists()
        print("1. Failing-control block: OK ->", result)

        # 2. All controls pass, file doesn't exist yet -> exports.
        real_controls = {"a": True, "b": True}
        result = do_export(output_path, False, True, real_controls, summary_report, detail_report)
        assert result.startswith("EXPORTED"), result
        assert output_path.exists()
        print("2. Fresh export: OK ->", result)
        mtime_1 = output_path.stat().st_mtime_ns

        # 3. File now exists, overwrite not confirmed -> blocked, file untouched.
        result = do_export(output_path, False, True, real_controls, summary_report, detail_report)
        assert result == "BLOCKED: exists, no overwrite confirmation", result
        assert output_path.stat().st_mtime_ns == mtime_1
        print("3. Existing-file block (no overwrite confirm): OK ->", result)

        # 4. Overwrite confirmed -> re-exports.
        result = do_export(output_path, True, True, real_controls, summary_report, detail_report)
        assert result.startswith("EXPORTED"), result
        print("4. Confirmed overwrite: OK ->", result)

        # 5. Reopen and verify sheets/columns/counts/totals.
        reopened = pd.read_excel(output_path, sheet_name=None)
        assert list(reopened.keys()) == ["Summary by Country", "Detail"]
        assert list(reopened["Summary by Country"].columns) == list(summary_report.columns)
        assert list(reopened["Detail"].columns) == list(detail_report.columns)
        assert len(reopened["Detail"]) == len(detail_report) == 216
        assert len(reopened["Summary by Country"]) == len(summary_report) == 6
        assert abs(reopened["Detail"]["Expense"].sum() - detail_report["Expense"].sum()) < 1e-6
        assert abs(reopened["Summary by Country"]["Expense: SUM"].sum() - summary_report["Expense: SUM"].sum()) < 1e-6
        print("5. Reopened-workbook verification: OK")
        print("\nSummary by Country:")
        print(reopened["Summary by Country"].to_string(index=False))

        print("\nALL EXPORT-LOGIC TESTS PASSED")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
