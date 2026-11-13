# Assignment 1 — Accounting Automation with Python

## Objective

Use Claude Code, Python, and marimo to automate an accounting workflow traditionally performed in Alteryx.

The objective is to understand how programming and artificial intelligence can be used to clean, transform, combine, and analyze accounting data.

## Provided files

- Automation Build Challenge - NA.xlsx
- Automation Build Challenge - SA.xlsx
- Automation Build Challenge - Managers.xlsx

## Business scenario

You have received expense reports from North America and South America, along with information about country managers and their team sizes.

Management requires a consolidated accounting report containing monthly expenses and summarized financial information by country.

## Tasks

1. Import and inspect the Excel files.
2. Identify and remove unnecessary information.
3. Clean and standardize the expense data.
4. Restructure the monthly expense records.
5. Combine North American and South American expenses.
6. Clean and prepare the manager information.
7. Match expenses with the corresponding managers.
8. Calculate total expenses and maximum team size by country and manager.
9. Export the results into an Excel workbook.
10. Validate the accuracy of your results.

## Required outputs

Your final Excel workbook must contain two worksheets.

### Summary by Country

- Country
- Manager
- Expense: SUM
- Team Size: MAX

### Detail

- Country
- Date
- Expense
- Manager
- Team Size

## Instructions

- Review the source files before writing code.
- Develop a workflow plan using plain English.
- Use Claude Code as your programming tutor.
- Complete one transformation at a time.
- Explain what each transformation accomplishes.
- Display intermediate results in your marimo notebook.
- Verify record counts and financial totals.
- Do not modify the original Excel files.
- Do not hardcode your results.

## Getting started

Open your repository in Visual Studio Code.

Run the following command in the terminal:

`uv sync`

To open marimo, run:

`uv run marimo edit`

Open Claude Code and explain the accounting problem in your own words.

## Deliverables

- A written workflow plan.
- A completed marimo Python notebook.
- A final Excel workbook containing both reports.
- A brief explanation of how you validated your accounting results.
- A short reflection on your experience using AI-assisted programming.

## Submission

Commit and push your notebook, workflow plan, and reflection to your private GitHub repository.

Submit the generated Excel workbook through the instructor-approved submission method.

Make sure your instructor and research assistant have access to your repository.
