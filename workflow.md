# Workflow plan — Assignment 1

## My intended workflow (as given to the assistant)

I provided three Excel files (North America expenses, South America expenses,
manager information) and described this workflow in natural language:

1. Identify the actual financial tables in each workbook and remove
   unnecessary headers, blank rows, and irrelevant/decorative information.
2. Clean and standardize the expense data.
3. Restructure the monthly expense columns into individual rows containing
   country, date, and expense amount (unpivot).
4. Combine the North American and South American expense records.
5. Clean the manager information, including team sizes.
6. Match each expense record with the correct manager and team size.
7. Produce two reports:
   - **Summary by Country**: Country, Manager, Expense: SUM, Team Size: MAX
   - **Detail**: Country, Date, Expense, Manager, Team Size

I also asked that the workflow preserve the original datasets, avoid
hardcoding financial results, and validate that no records or amounts were
lost or duplicated.

No drawing was supplied — this plan was given as text.

## Assistant's interpretation and one clarified discrepancy

My original message asked for "two separate Excel outputs" (two downloadable
files). `assignment.md` for this course assignment specifies a single
workbook (`submission/assignment_1.xlsx`) containing exactly two worksheets
("Summary by Country" and "Detail") with the exact column sets above. The
notebook therefore implements **one workbook with two sheets**, matching the
graded deliverable, rather than two separate files. This is the only point
where the assistant's implementation diverges from my literal wording, and it
was flagged to me rather than decided silently.

## Matching rule

Expense records are matched to managers on **Country**, using the "North
America" and "South America" sheets of the Managers workbook (the "Europe"
sheet has no corresponding expense data and is carried as an unused reference,
reported separately rather than merged in).

## Revisions

None yet — this file will be updated if I change the plan after reviewing the
notebook's intermediate tables.
