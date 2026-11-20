"""Independent cross-check of the notebook's parsing/combining/matching logic.

Re-implements the same structural-detection parser (copied from
notebooks/assignment_1.py) and compares its totals against a brute-force,
hardcoded-index read of the same workbooks, plus checks the manager join.
Read-only; writes nothing.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_expense_workbook(path, source_label):
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

    date_row_idx, date_cols = None, []
    for r_idx, row in enumerate(rows):
        dt_cols = [c for c, val in enumerate(row) if isinstance(val, datetime)]
        if len(dt_cols) > len(date_cols):
            date_row_idx, date_cols = r_idx, dt_cols
    dates = {c: rows[date_row_idx][c] for c in date_cols}

    records = []
    for r_idx in range(country_header_row + 1, len(rows)):
        raw_country = rows[r_idx][country_col]
        if raw_country is None or (isinstance(raw_country, str) and raw_country.strip() == ""):
            continue
        country = raw_country.strip() if isinstance(raw_country, str) else raw_country
        for c_idx, dt in dates.items():
            records.append({"country": country, "date": dt, "expense": rows[r_idx][c_idx]})
    return pd.DataFrame.from_records(records)


def brute_force_sums():
    expected_rows = {
        "starter_data/Automation Build Challenge - NA.xlsx": (11, 13, 15),
        "starter_data/Automation Build Challenge - SA.xlsx": (11, 13, 15),
    }
    totals = {}
    for fname, row_idxs in expected_rows.items():
        wb = openpyxl.load_workbook(REPO_ROOT / fname, read_only=True, data_only=True)
        ws = wb[wb.sheetnames[0]]
        rows = list(ws.iter_rows(values_only=True))
        for r in row_idxs:
            country = rows[r][2]
            vals = [v for v in rows[r][5:41] if isinstance(v, (int, float))]
            totals[country] = sum(vals)
    return totals


def main():
    na = parse_expense_workbook(REPO_ROOT / "starter_data/Automation Build Challenge - NA.xlsx", "NA")
    sa = parse_expense_workbook(REPO_ROOT / "starter_data/Automation Build Challenge - SA.xlsx", "SA")
    combined = pd.concat([na, sa], ignore_index=True)

    assert len(combined) == 216, f"expected 216 rows, got {len(combined)}"
    assert combined["expense"].isna().sum() == 0, "unexpected missing expense values"
    assert not combined.duplicated(subset=["country", "date"]).any(), "unexpected duplicate rows"

    parser_sums = combined.groupby("country")["expense"].sum().to_dict()
    brute_sums = brute_force_sums()

    assert set(parser_sums) == set(brute_sums), (set(parser_sums), set(brute_sums))
    for country in brute_sums:
        diff = abs(parser_sums[country] - brute_sums[country])
        assert diff < 1e-6, f"{country}: parser={parser_sums[country]} brute={brute_sums[country]}"

    print("Row count: 216 OK")
    print("No missing/duplicate rows: OK")
    print("Per-country sums match brute-force hardcoded read:")
    for country, total in sorted(parser_sums.items()):
        print(f"  {country}: {total}")
    print(f"Grand total: {combined['expense'].sum()}")

    # Manager join cross-check
    managers = pd.concat(
        [df.assign(source_sheet=name) for name, df in pd.read_excel(
            REPO_ROOT / "starter_data/Automation Build Challenge - Managers.xlsx", sheet_name=None
        ).items()],
        ignore_index=True,
    )
    managers["country"] = managers["Country"].astype(str).str.strip()

    def extract_team_size(v):
        if isinstance(v, (int, float)) and not pd.isna(v):
            return float(v)
        m = re.search(r"\d+", str(v))
        return float(m.group()) if m else np.nan

    managers["team_size"] = managers["Team Size"].apply(extract_team_size)
    assert managers["team_size"].isna().sum() == 0, "a Team Size cell failed to parse"
    assert not managers.duplicated(subset=["country"]).any(), "duplicate manager country rows"

    expense_countries = set(combined["country"].unique())
    manager_countries = set(managers["country"].unique())
    unmatched = expense_countries - manager_countries
    assert not unmatched, f"unmatched expense countries: {unmatched}"

    unused = managers[~managers["country"].isin(expense_countries)]
    print(f"\nManager rows with no matching expenses (expected: Europe sheet, 4 rows): {len(unused)}")
    print(sorted(unused["country"].tolist()))
    print("\nTeam sizes parsed:")
    print(managers[["country", "Team Size", "team_size", "source_sheet"]].to_string(index=False))

    print("\nALL INDEPENDENT CHECKS PASSED")


if __name__ == "__main__":
    sys.exit(main())
