# Assignment 1: Accounting automation through vibe coding

## Objective

Independently recreate an accounting workflow using AI-generated Python in
Marimo. You already know Marimo; concentrate on accounting logic, workflow
design, communicating with AI, inspecting results, and financial validation.
Manual Python coding is not required. The lecture demonstration uses a separate
example and is not the solution to this assignment.

## Accounting problem

You have received expense reports from North America and South America, along
with country managers and their team sizes. Management needs a consolidated
monthly expense report and summarized financial information by country and
manager. Use the three unchanged Excel workbooks in [starter_data/](./starter_data/),
described in its [data guide](./starter_data/README.md).

The final Excel workbook must contain exactly these two worksheets and columns:

| Worksheet | Required columns, in order |
| --- | --- |
| Summary by Country | Country, Manager, Expense: SUM, Team Size: MAX |
| Detail | Country, Date, Expense, Manager, Team Size |

The summary must report total expenses and maximum team size by country and
manager. Decide how to prepare and connect the supplied information; do not
copy an instructor or another student's implementation. Clarify any material
accounting ambiguity rather than inventing rules or missing data.

## Your responsibilities

1. Understand the accounting problem and inspect the source workbooks.
2. Independently draw or describe your intended workflow. Explain your inputs,
   accounting transformations, matching rules, calculations, outputs, and checks.
3. Communicate that plan to Claude or Codex before asking for implementation.
   Review AI's interpretation and correct misunderstandings.
4. Ask AI to generate, execute, debug, and validate an executable Marimo notebook.
   It may complete the whole workflow; individual transformations do not need
   separate approval. You remain responsible for the accounting decisions.
5. Inspect intermediate accounting datasets and investigate missing values,
   duplicates, unmatched records, changed counts, and unexpected totals.
6. Validate source-to-report financial totals and explain the evidence. Preserve
   source precision, document rounding/currency assumptions and any tolerance,
   and verify that joins do not duplicate or lose expense records. Compare with
   original Alteryx output if provided; otherwise mark that comparison unavailable.
7. Review final reports, intentionally export a new Excel workbook only when
   critical checks pass, and reopen it to verify the exported results. Do not
   automatically overwrite files or change the original datasets.
8. Reflect in your own words on your experience communicating with AI, decisions
   you made, revisions, mistakes found, and limitations of your validation.

## Notebook requirements

- Clearly labeled accounting transformations in separate logical-stage cells.
- Interactive tables showing intermediate datasets and final reports.
- A visual workflow diagram and real cell dependencies inspectable in Marimo.
- Simple explanations of accounting purposes and equivalent Alteryx tools.
- Record counts, missing-value and duplicate checks, matching exceptions, and
  financial reconciliation checks at meaningful stages.
- An intentional Excel export action that is blocked by critical failed checks
  and does not silently overwrite prior reports.
- Accessible Python code for inspection; manually writing it is not required.

Never hardcode financial answers or silently adjust source values to make checks
pass. A passing check must be supported by actual data, not an AI assurance.

## Deliverables and submission

Submit your generated `notebooks/assignment_1.py`, your plan in `workflow.md`,
your drawing under `workflow/` if used, actual validation evidence in
`validation.md`, the final workbook `submission/assignment_1.xlsx`, and your own
`reflection.md`. Include important workflow revisions and unresolved questions.

Follow the [README](./README.md) for environment setup, notebook commands, and
GitHub submission. Commit and push the deliverables to your own private repository;
submit its URL and final commit identifier through the course channel. Invite
Professor Julia Kokina and the research assistant using the usernames supplied
by the course, and confirm both accepted. Do not grant classmates access.
