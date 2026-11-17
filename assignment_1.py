import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import re
    from pathlib import Path

    import pandas as pd

    return Path, pd, re


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Assignment 1 — Consolidated Expense Report

    We have three source workbooks:

    - **NA workbook** — monthly expenses for Canada, Mexico, United States
    - **SA workbook** — monthly expenses for Brazil, Chile, Colombia
    - **Managers workbook** — manager name and team size per country

    Goal: produce one Excel report with a **Summary by Country** sheet
    (total expense and max team size per country/manager) and a
    **Detail** sheet (every monthly expense line tagged with its manager
    and team size).
    """)
    return


@app.cell
def _(mo):
    mo.mermaid(
        """
        flowchart TD
            A[Load NA workbook] --> C[Strip junk rows, extract Country x Month table]
            B[Load SA workbook] --> D[Strip junk rows, extract Country x Month table]
            C --> E[Unpivot NA: months -> rows]
            D --> F[Unpivot SA: months -> rows]
            E --> G[Combine NA + SA expenses]
            F --> G
            H[Load Managers workbook, 3 sheets] --> I[Stack NA / Europe / SA sheets]
            I --> J[Clean Team Size text into numbers]
            G --> K[Join expenses to managers on Country]
            J --> K
            K --> L[Detail report]
            K --> M[Summary by Country report]
            L --> N[Export to Excel]
            M --> N
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 1 — Load the source files
    """)
    return


@app.cell
def _(Path):
    DATA_DIR = Path("starter_data")
    NA_FILE = DATA_DIR / "Automation Build Challenge - NA.xlsx"
    SA_FILE = DATA_DIR / "Automation Build Challenge - SA.xlsx"
    MANAGERS_FILE = DATA_DIR / "Automation Build Challenge - Managers.xlsx"
    return MANAGERS_FILE, NA_FILE, SA_FILE


@app.cell
def _(mo):
    mo.md("""
    ## Step 2 & 3 — Remove unnecessary information, clean the expense data

    Each expense workbook has a decorative title block (fake labels like
    "WASTED SPACE" and "Hidden Value") above the real table, and the real
    table lists one row per country with one column per month. The
    function below finds the real table by locating the `Date>>>` marker
    and the `Country` label, so nothing about the layout is hardcoded.
    """)
    return


@app.cell
def _(pd):
    def extract_expense_table(path, region_name):
        """Read the Country x Month expense block, ignoring the decorative header rows."""
        raw = pd.read_excel(path, sheet_name="Sheet1", header=None)

        date_marker_rows = raw.index[raw.eq("Date>>>").any(axis=1)]
        date_row_idx = date_marker_rows[0]
        date_row = raw.loc[date_row_idx]
        date_start_col = date_row[date_row == "Date>>>"].index[0] + 1
        dates = date_row.loc[date_start_col:].dropna()
        date_cols = dates.index.tolist()

        below_header = raw.loc[date_row_idx + 1:]
        country_col = next(
            col for col in raw.columns if (below_header[col] == "Country").any()
        )

        has_country_name = below_header[country_col].notna() & (
            below_header[country_col] != "Country"
        )
        has_expense_numbers = below_header[date_cols].notna().any(axis=1)
        country_rows = below_header[has_country_name & has_expense_numbers]

        table = country_rows[[country_col] + date_cols].copy()
        table.columns = ["Country"] + list(dates.values)
        table.insert(1, "Region", region_name)
        return table.reset_index(drop=True)

    return (extract_expense_table,)


@app.cell
def _(NA_FILE, extract_expense_table):
    na_wide = extract_expense_table(NA_FILE, "North America")
    na_wide
    return (na_wide,)


@app.cell
def _(SA_FILE, extract_expense_table):
    sa_wide = extract_expense_table(SA_FILE, "South America")
    sa_wide
    return (sa_wide,)


@app.cell
def _(na_wide, sa_wide):
    source_total = round(
        na_wide.drop(columns=["Country", "Region"]).sum().sum()
        + sa_wide.drop(columns=["Country", "Region"]).sum().sum(),
        2,
    )
    return (source_total,)


@app.cell
def _(mo):
    mo.md("""
    ## Step 4 — Restructure the monthly expense records (unpivot)

    Each country currently has 36 expense columns (one per month). We
    reshape this into one row per Country + Month, which is the format
    needed for joining, summing, and reporting. This is the equivalent
    of Alteryx's **Transpose** tool.
    """)
    return


@app.cell
def _(pd):
    def unpivot_expenses(wide_table):
        long_table = wide_table.melt(
            id_vars=["Country", "Region"], var_name="Date", value_name="Expense"
        )
        long_table["Date"] = pd.to_datetime(long_table["Date"])
        long_table["Expense"] = long_table["Expense"].round(2)
        return long_table

    return (unpivot_expenses,)


@app.cell
def _(na_wide, unpivot_expenses):
    na_long = unpivot_expenses(na_wide)
    na_long.head(10)
    return (na_long,)


@app.cell
def _(sa_wide, unpivot_expenses):
    sa_long = unpivot_expenses(sa_wide)
    sa_long.head(10)
    return (sa_long,)


@app.cell
def _(mo):
    mo.md("""
    ## Step 5 — Combine North America and South America

    Equivalent of Alteryx's **Union** tool: stack both regions into one
    expense table.
    """)
    return


@app.cell
def _(na_long, pd, sa_long):
    expenses_combined = pd.concat([na_long, sa_long], ignore_index=True)
    expenses_combined["Country"] = expenses_combined["Country"].str.strip()
    expenses_combined
    return (expenses_combined,)


@app.cell
def _(expenses_combined, mo, source_total):
    combined_total = round(expenses_combined["Expense"].sum(), 2)
    totals_match = combined_total == source_total
    mo.md(
        f"""
        **Validation check 1 — Reshape did not lose or duplicate dollars**

        - Source total (NA + SA raw monthly columns): ${source_total:,.2f}
        - Combined long-format total: ${combined_total:,.2f}
        - Match: {"Yes" if totals_match else "No — investigate"}
        - Row count: {len(expenses_combined)} monthly expense records
        """
    )
    return (combined_total,)


@app.cell
def _(mo):
    mo.md("""
    ## Step 6 — Clean and prepare the manager information

    The Managers workbook has three sheets (North America, Europe, South
    America). We stack them into one table, trim stray spaces from
    Country/Manager text, and convert the inconsistent `Team Size` text
    ("135 EE", "team of 15", "10 Persons") into plain numbers.
    """)
    return


@app.cell
def _(MANAGERS_FILE, pd):
    managers_raw = pd.read_excel(MANAGERS_FILE, sheet_name=None)
    managers_stacked = pd.concat(
        [df.assign(Region=region) for region, df in managers_raw.items()],
        ignore_index=True,
    )
    managers_stacked
    return (managers_stacked,)


@app.cell
def _(re):
    def extract_team_size(value):
        """Pull the first number out of free-text team size descriptions."""
        match = re.search(r"\d+", str(value))
        return int(match.group()) if match else None

    return (extract_team_size,)


@app.cell
def _(extract_team_size, managers_stacked):
    managers_clean = managers_stacked.copy()
    managers_clean["Country"] = managers_clean["Country"].str.strip()
    managers_clean["Manager"] = managers_clean["Manager"].str.strip()
    managers_clean["Team Size"] = managers_clean["Team Size"].apply(extract_team_size)
    managers_clean
    return (managers_clean,)


@app.cell
def _(managers_clean, mo):
    duplicate_manager_countries = managers_clean[
        managers_clean.duplicated("Country", keep=False)
    ]
    mo.md(
        f"""
        **Validation check 2 — One manager per country**

        Duplicate country rows in the manager table (would inflate the
        join): {len(duplicate_manager_countries)}
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 7 — Match expenses with managers

    Equivalent of Alteryx's **Join** tool: attach Manager and Team Size
    to every expense row based on Country. We use a left join so any
    expense row without a matching manager is kept and flagged, not
    silently dropped.
    """)
    return


@app.cell
def _(expenses_combined, managers_clean):
    expenses_with_managers = expenses_combined.merge(
        managers_clean[["Country", "Manager", "Team Size"]], on="Country", how="left"
    )
    expenses_with_managers
    return (expenses_with_managers,)


@app.cell
def _(expenses_combined, expenses_with_managers, mo):
    rows_before_join = len(expenses_combined)
    rows_after_join = len(expenses_with_managers)
    unmatched = expenses_with_managers[expenses_with_managers["Manager"].isna()]
    duplicate_expense_rows = int(
        expenses_with_managers.duplicated(subset=["Country", "Date"]).sum()
    )

    mo.md(
        f"""
        **Validation check 3 — Join quality**

        - Expense rows before join: {rows_before_join}
        - Expense rows after join: {rows_after_join}
        - Row count unchanged (join did not duplicate records): {"Yes" if rows_before_join == rows_after_join else "No — investigate"}
        - Expense rows with no matching manager: {len(unmatched)}
        - Duplicate Country + Date combinations: {duplicate_expense_rows}
        """
    )
    return


@app.cell
def _(expenses_combined, expenses_with_managers, mo):
    total_before_join = round(expenses_combined["Expense"].sum(), 2)
    total_after_join = round(expenses_with_managers["Expense"].sum(), 2)
    mo.md(
        f"""
        **Validation check 4 — Dollars unchanged by the join**

        - Total before join: ${total_before_join:,.2f}
        - Total after join: ${total_after_join:,.2f}
        - Match: {"Yes" if total_before_join == total_after_join else "No — investigate"}
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 8 & 9 — Build the reports and export to Excel
    """)
    return


@app.cell
def _(expenses_with_managers):
    detail_report = (
        expenses_with_managers[["Country", "Date", "Expense", "Manager", "Team Size"]]
        .sort_values(["Country", "Date"])
        .reset_index(drop=True)
    )
    detail_report
    return (detail_report,)


@app.cell
def _(detail_report):
    summary_report = (
        detail_report.groupby(["Country", "Manager"], as_index=False).agg(
            **{"Expense: SUM": ("Expense", "sum"), "Team Size: MAX": ("Team Size", "max")}
        )
    ).sort_values("Country").reset_index(drop=True)
    summary_report
    return (summary_report,)


@app.cell
def _(combined_total, detail_report, mo, summary_report):
    detail_total = round(detail_report["Expense"].sum(), 2)
    summary_total = round(summary_report["Expense: SUM"].sum(), 2)
    all_totals_match = detail_total == summary_total == combined_total

    mo.md(
        f"""
        **Validation check 5 — Final totals tie out**

        - Original combined expense total: ${combined_total:,.2f}
        - Detail report total: ${detail_total:,.2f}
        - Summary report total: ${summary_total:,.2f}
        - All three match: {"Yes" if all_totals_match else "No — investigate"}
        """
    )
    return


@app.cell
def _(Path):
    OUTPUT_DIR = Path("outputs")
    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE = OUTPUT_DIR / "Consolidated_Expense_Report.xlsx"
    return (OUTPUT_FILE,)


@app.cell
def _(OUTPUT_FILE, detail_report, pd, summary_report):
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        summary_report.to_excel(writer, sheet_name="Summary by Country", index=False)
        detail_report.to_excel(writer, sheet_name="Detail", index=False)
    return


@app.cell
def _(OUTPUT_FILE, mo):
    mo.md(f"""
    Report exported to `{OUTPUT_FILE}`
    """)
    return


if __name__ == "__main__":
    app.run()
